package main

import (
	"context"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"net"
	"os"
	"path/filepath"
	"reflect"
	"strconv"
	"strings"
	"time"

	apiAdvertiser "github.com/bububa/spotlight-mapi/api/advertiser"
	apiCampaign "github.com/bububa/spotlight-mapi/api/campaign"
	apiCreativity "github.com/bububa/spotlight-mapi/api/creativity"
	apiOffline "github.com/bububa/spotlight-mapi/api/report/offline"
	apiRealtime "github.com/bububa/spotlight-mapi/api/report/realtime"
	apiUnit "github.com/bububa/spotlight-mapi/api/unit"
	"github.com/bububa/spotlight-mapi/core"
	"github.com/bububa/spotlight-mapi/enum"
	"github.com/bububa/spotlight-mapi/model"
	modelAdvertiser "github.com/bububa/spotlight-mapi/model/advertiser"
	modelCampaign "github.com/bububa/spotlight-mapi/model/campaign"
	modelCreativity "github.com/bububa/spotlight-mapi/model/creativity"
	modelOffline "github.com/bububa/spotlight-mapi/model/report/offline"
	modelRealtime "github.com/bububa/spotlight-mapi/model/report/realtime"
	modelUnit "github.com/bububa/spotlight-mapi/model/unit"
)

type config struct {
	EnvPath       string
	OutputPath    string
	AccessToken   string
	AdvertiserID  uint64
	AppID         uint64
	AppSecret     string
	StartDate     string
	EndDate       string
	PageSize      int64
	MissingFields []string
}

type stepResult struct {
	Name          string
	Endpoint      string
	Status        string
	ErrorType     string
	Error         string
	Summary       string
	ResponseShape any
}

type spikeReport struct {
	GeneratedAt  string
	EnvPath      string
	TokenStatus  string
	AdvertiserID string
	DateRange    string
	Steps        []stepResult
}

var redactionTokens []string

func main() {
	defaultEnv := filepath.Join("config", "private", "xhs", ".env")
	defaultOutput := filepath.Join("outputs", "xiaohongshu", "xhs_api_readonly_spike.md")
	envPath := flag.String("env", defaultEnv, "path to local private env file")
	outputPath := flag.String("output", defaultOutput, "path to markdown output")
	flag.Parse()

	cfg := loadConfig(*envPath, *outputPath)
	redactionTokens = append(redactionTokens, cfg.AccessToken, cfg.AppSecret)
	report := spikeReport{
		GeneratedAt:  time.Now().Format(time.RFC3339),
		EnvPath:      cfg.EnvPath,
		TokenStatus:  tokenStatus(cfg.AccessToken),
		AdvertiserID: redactID(cfg.AdvertiserID),
		DateRange:    cfg.StartDate + " to " + cfg.EndDate,
	}

	if len(cfg.MissingFields) > 0 {
		report.Steps = append(report.Steps, stepResult{
			Name:      "env validation",
			Endpoint:  "local env",
			Status:    "blocked",
			ErrorType: "env 缺失",
			Error:     "missing required env: " + strings.Join(cfg.MissingFields, ", "),
			Summary:   "未读取完整本地私密配置，未发起任何 API 请求。",
		})
	} else {
		report.Steps = runReadOnlyChecks(cfg)
	}

	if err := writeMarkdown(cfg.OutputPath, report); err != nil {
		fmt.Fprintf(os.Stderr, "write output failed: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("xhs read-only spike finished\n")
	fmt.Printf("env_path=%s\n", cfg.EnvPath)
	fmt.Printf("token_status=%s\n", cfg.TokenStatus())
	fmt.Printf("advertiser_id=%s\n", redactID(cfg.AdvertiserID))
	fmt.Printf("output=%s\n", cfg.OutputPath)
}

func loadConfig(envPath string, outputPath string) config {
	values := map[string]string{}
	if b, err := os.ReadFile(envPath); err == nil {
		values = parseDotEnv(string(b))
	}
	for _, key := range []string{
		"XHS_ACCESS_TOKEN",
		"XHS_ADVERTISER_ID",
		"XHS_APP_ID",
		"XHS_APP_SECRET",
		"XHS_REPORT_START_DATE",
		"XHS_REPORT_END_DATE",
		"XHS_PAGE_SIZE",
	} {
		if v := os.Getenv(key); v != "" {
			values[key] = v
		}
	}

	yesterday := time.Now().AddDate(0, 0, -1).Format("2006-01-02")
	pageSize := int64(10)
	if raw := values["XHS_PAGE_SIZE"]; raw != "" {
		if n, err := strconv.ParseInt(raw, 10, 64); err == nil && n > 0 {
			pageSize = n
		}
	}

	cfg := config{
		EnvPath:     envPath,
		OutputPath:  outputPath,
		AccessToken: strings.TrimSpace(values["XHS_ACCESS_TOKEN"]),
		AppSecret:   strings.TrimSpace(values["XHS_APP_SECRET"]),
		StartDate:   firstNonEmpty(values["XHS_REPORT_START_DATE"], yesterday),
		EndDate:     firstNonEmpty(values["XHS_REPORT_END_DATE"], yesterday),
		PageSize:    pageSize,
	}
	cfg.AdvertiserID = parseUint(values["XHS_ADVERTISER_ID"])
	cfg.AppID = parseUint(values["XHS_APP_ID"])

	if cfg.AccessToken == "" {
		cfg.MissingFields = append(cfg.MissingFields, "XHS_ACCESS_TOKEN")
	}
	if cfg.AdvertiserID == 0 {
		cfg.MissingFields = append(cfg.MissingFields, "XHS_ADVERTISER_ID")
	}
	return cfg
}

func (c config) TokenStatus() string {
	return tokenStatus(c.AccessToken)
}

func parseDotEnv(content string) map[string]string {
	values := map[string]string{}
	for _, line := range strings.Split(content, "\n") {
		line = strings.TrimSpace(line)
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		key, value, ok := strings.Cut(line, "=")
		if !ok {
			continue
		}
		key = strings.TrimSpace(key)
		value = strings.TrimSpace(value)
		value = strings.Trim(value, `"'`)
		values[key] = value
	}
	return values
}

func runReadOnlyChecks(cfg config) []stepResult {
	ctx, cancel := context.WithTimeout(context.Background(), 90*time.Second)
	defer cancel()

	client := core.NewSDKClient(cfg.AppID, cfg.AppSecret)
	page := &model.PageDTO{PageIndex: 1, PageSize: cfg.PageSize}
	commonOfflineReq := func() *modelOffline.Request {
		return &modelOffline.Request{
			AdvertiserID: cfg.AdvertiserID,
			StartDate:    cfg.StartDate,
			EndDate:      cfg.EndDate,
			TimeUnit:     enum.TimeUnit_DAY,
			PageNum:      1,
			PageSize:     cfg.PageSize,
		}
	}

	var steps []stepResult
	steps = append(steps, runStep("account balance", "GET /jg/account/balance/info", func() (string, any, error) {
		ret, err := apiAdvertiser.BalanceInfo(ctx, client, &modelAdvertiser.BalanceInfoRequest{AdvertiserID: cfg.AdvertiserID}, cfg.AccessToken)
		if err != nil {
			return "", nil, err
		}
		return "账号余额接口可读；金额值未写入报告，只确认返回结构。", ret, nil
	}))
	steps = append(steps, runStep("campaign list", "POST /jg/campaign/list", func() (string, any, error) {
		ret, err := apiCampaign.List(ctx, client, &modelCampaign.ListRequest{AdvertiserID: cfg.AdvertiserID, Page: page}, cfg.AccessToken)
		if err != nil {
			return "", nil, err
		}
		count := 0
		if ret != nil {
			count = len(ret.Campaigns)
		}
		return fmt.Sprintf("计划列表可读；本页返回 %d 条。", count), summarizeIDs(ret, "campaign"), nil
	}))
	steps = append(steps, runStep("unit list", "POST /jg/unit/list", func() (string, any, error) {
		ret, err := apiUnit.List(ctx, client, &modelUnit.ListRequest{AdvertiserID: cfg.AdvertiserID, Page: 1, PageSize: int(cfg.PageSize)}, cfg.AccessToken)
		if err != nil {
			return "", nil, err
		}
		count := 0
		if ret != nil {
			count = len(ret.UnitInfos)
		}
		return fmt.Sprintf("单元列表可读；本页返回 %d 条。", count), summarizeIDs(ret, "unit"), nil
	}))
	steps = append(steps, runStep("creativity search", "POST /jg/creativity/search", func() (string, any, error) {
		ret, err := apiCreativity.Search(ctx, client, &modelCreativity.SearchRequest{AdvertiserID: cfg.AdvertiserID, Page: page}, cfg.AccessToken)
		if err != nil {
			return "", nil, err
		}
		count := 0
		if ret != nil {
			count = len(ret.Creativities)
		}
		return fmt.Sprintf("创意查询可读；本页返回 %d 条。", count), summarizeIDs(ret, "creativity"), nil
	}))
	steps = append(steps, runStep("offline report advertiser", "POST /jg/data/report/offline/account", func() (string, any, error) {
		ret, err := apiOffline.Advertiser(ctx, client, commonOfflineReq(), cfg.AccessToken)
		return reportSummary("账户层级离线报表", ret, err)
	}))
	steps = append(steps, runStep("offline report campaign", "POST /jg/data/report/offline/campaign", func() (string, any, error) {
		ret, err := apiOffline.Campaign(ctx, client, commonOfflineReq(), cfg.AccessToken)
		return reportSummary("计划层级离线报表", ret, err)
	}))
	steps = append(steps, runStep("offline report unit", "POST /jg/data/report/offline/unit", func() (string, any, error) {
		ret, err := apiOffline.Unit(ctx, client, commonOfflineReq(), cfg.AccessToken)
		return reportSummary("单元层级离线报表", ret, err)
	}))
	steps = append(steps, runStep("offline report creativity", "POST /jg/data/report/offline/creativity", func() (string, any, error) {
		ret, err := apiOffline.Creativity(ctx, client, commonOfflineReq(), cfg.AccessToken)
		return reportSummary("创意层级离线报表", ret, err)
	}))
	steps = append(steps, runStep("realtime report advertiser", "POST /jg/data/report/realtime/account", func() (string, any, error) {
		ret, err := apiRealtime.Advertiser(ctx, client, &modelRealtime.AdvertiserRequest{AdvertiserID: cfg.AdvertiserID, StartDate: cfg.EndDate, EndDate: cfg.EndDate}, cfg.AccessToken)
		if err != nil {
			return "", nil, err
		}
		return "账户层级实时报表可读。", ret, nil
	}))
	steps = append(steps, runStep("realtime report campaign", "POST /jg/data/report/realtime/campaign", func() (string, any, error) {
		ret, err := apiRealtime.Campaign(ctx, client, &modelRealtime.CampaignRequest{AdvertiserID: cfg.AdvertiserID, StartDate: cfg.EndDate, EndDate: cfg.EndDate, PageNum: 1, PageSize: cfg.PageSize}, cfg.AccessToken)
		if err != nil {
			return "", nil, err
		}
		return fmt.Sprintf("计划层级实时报表可读；本页返回 %d 条。", len(ret.CampaignDTOs)), summarizeIDs(ret, "campaign_realtime"), nil
	}))
	steps = append(steps, runStep("realtime report unit", "POST /jg/data/report/realtime/unit", func() (string, any, error) {
		ret, err := apiRealtime.Unit(ctx, client, &modelRealtime.UnitRequest{AdvertiserID: cfg.AdvertiserID, StartDate: cfg.EndDate, EndDate: cfg.EndDate, PageNum: 1, PageSize: cfg.PageSize}, cfg.AccessToken)
		if err != nil {
			return "", nil, err
		}
		return fmt.Sprintf("单元层级实时报表可读；本页返回 %d 条。", len(ret.UnitDTOs)), summarizeIDs(ret, "unit_realtime"), nil
	}))
	steps = append(steps, runStep("realtime report creativity", "POST /jg/data/report/realtime/creativity", func() (string, any, error) {
		ret, err := apiRealtime.Creativity(ctx, client, &modelRealtime.CreativityRequest{AdvertiserID: cfg.AdvertiserID, StartDate: cfg.EndDate, EndDate: cfg.EndDate, PageNum: 1, PageSize: cfg.PageSize}, cfg.AccessToken)
		if err != nil {
			return "", nil, err
		}
		return fmt.Sprintf("创意层级实时报表可读；本页返回 %d 条。", len(ret.CreativityDTOs)), summarizeIDs(ret, "creativity_realtime"), nil
	}))
	return steps
}

type readStep func() (summary string, shape any, err error)

func runStep(name string, endpoint string, fn readStep) stepResult {
	summary, shape, err := fn()
	if err != nil {
		return stepResult{
			Name:      name,
			Endpoint:  endpoint,
			Status:    "failed",
			ErrorType: classifyError(err),
			Error:     sanitizeError(err),
			Summary:   "接口调用失败，继续尝试后续 read-only 接口。",
		}
	}
	return stepResult{
		Name:          name,
		Endpoint:      endpoint,
		Status:        "ok",
		Summary:       summary,
		ResponseShape: shape,
	}
}

func reportSummary(label string, ret *modelOffline.ReportList, err error) (string, any, error) {
	if err != nil {
		return "", nil, err
	}
	count := 0
	total := int64(0)
	if ret != nil {
		count = len(ret.List)
		total = ret.TotalCount
	}
	return fmt.Sprintf("%s 可读；本页返回 %d 条，总数 %d。", label, count, total), summarizeIDs(ret, "offline_report"), nil
}

func writeMarkdown(path string, report spikeReport) error {
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return err
	}
	var b strings.Builder
	b.WriteString("# 小红书聚光 API Read-only Spike\n\n")
	b.WriteString("## 运行摘要\n\n")
	b.WriteString("- 生成时间: " + report.GeneratedAt + "\n")
	b.WriteString("- 私密 env 路径: `" + report.EnvPath + "`\n")
	b.WriteString("- token 状态: `" + report.TokenStatus + "`\n")
	b.WriteString("- advertiser_id: `" + report.AdvertiserID + "`\n")
	b.WriteString("- 报表日期范围: `" + report.DateRange + "`\n")
	b.WriteString("- 安全边界: 本 spike 只调用 SDK 中的 read-only 列表、账号余额和报表接口；未调用创建、编辑、状态修改、删除、转化回传接口。\n\n")

	b.WriteString("## 接口验证结果\n\n")
	b.WriteString("| Step | Endpoint | Status | Error Type | Summary |\n")
	b.WriteString("|---|---|---:|---|---|\n")
	for _, step := range report.Steps {
		b.WriteString("| " + escapeMD(step.Name) + " | `" + step.Endpoint + "` | " + step.Status + " | " + escapeMD(step.ErrorType) + " | " + escapeMD(firstNonEmpty(step.Summary, step.Error)) + " |\n")
	}
	b.WriteString("\n")

	if hasFailures(report.Steps) {
		b.WriteString("## 失败明细\n\n")
		for _, step := range report.Steps {
			if step.Status != "ok" {
				b.WriteString("- `" + step.Name + "`: " + firstNonEmpty(step.ErrorType, "unknown") + " - " + escapeMD(step.Error) + "\n")
			}
		}
		b.WriteString("\n")
	}

	b.WriteString("## 小红书对象层级\n\n")
	b.WriteString("基于 `github.com/bububa/spotlight-mapi` v1.1.2 的 SDK 模型，聚光投放对象层级可以按以下方式理解：\n\n")
	b.WriteString("```text\n")
	b.WriteString("advertiser\n")
	b.WriteString("  -> campaign\n")
	b.WriteString("      -> unit\n")
	b.WriteString("          -> creativity\n")
	b.WriteString("          -> keyword (搜索推广/关键词场景)\n")
	b.WriteString("```\n\n")
	b.WriteString("- `campaign` 列表返回 `campaign_id`、`campaign_name`、营销目标、投放类型、优化目标、投放标的、预算和时段等字段。\n")
	b.WriteString("- `unit` 列表返回 `id`、`campaign_id`、`name`、出价、落地页、笔记/商品/直播间标的、关键词选词配置等字段。\n")
	b.WriteString("- `creativity` 查询返回 `creative_id`、`creative_name`、`campaign_id`、`unit_id`、`note_id`、`image`、`jump_url`、`page_id`、组件类型、审核状态等字段。\n")
	b.WriteString("- 离线报表维度返回 `time`、`campaign_id`、`unit_id`、`creativity_id`、`creativity_image`、`note_id`、`keyword_id`、`keyword` 等维度字段。\n\n")

	b.WriteString("## 稳定 ID 判断\n\n")
	b.WriteString("| 对象 | 稳定 ID | 说明 |\n")
	b.WriteString("|---|---|---|\n")
	b.WriteString("| advertiser | `advertiser_id` | 账号/广告主级调用必需。 |\n")
	b.WriteString("| campaign | `campaign_id` | 列表和报表均支持。 |\n")
	b.WriteString("| unit | `unit_id` / unit list 中 `id` | 单元列表字段名是 `id`，报表和实时模型使用 `unit_id`。 |\n")
	b.WriteString("| creativity | `creative_id` / 报表中 `creativity_id` | 创意查询字段名是 `creative_id`，报表维度使用 `creativity_id`。 |\n")
	b.WriteString("| note | `note_id` | 创意和报表均可能返回，可作为后续素材映射候选字段，但需要 Architecture 判断。 |\n")
	b.WriteString("| keyword | `keyword_id` / `keyword` | 关键词报表模型支持，仅适用于搜索/关键词场景。 |\n\n")

	b.WriteString("## 报表粒度与指标\n\n")
	b.WriteString("- 离线报表支持账户、计划、单元、创意、关键词层级；请求支持 `time_unit=DAY/HOUR/SUMMARY`，因此理论上最细可到 `date/hour + creativity_id/unit_id/campaign_id`，实际权限和平台参数仍需用真实 token 验证。\n")
	b.WriteString("- 实时报表支持账户、计划、单元、创意、关键词层级，返回对象属性加指标聚合。\n")
	b.WriteString("- 常见投放指标在 SDK `DataReportDTO` 中存在：`fee`(spend)、`impression`、`click`、`ctr`、`cpm`、`acp`、互动、行动按钮点击、表单、有效表单、私信、外链转化、ROI、电商订单等。\n")
	b.WriteString("- SDK 未直接使用 Meta 风格的 `spend` 字段名，小红书消费字段是 `fee`，后续统一事实表需要字段口径映射。\n\n")

	b.WriteString("## 创意到素材映射观察\n\n")
	b.WriteString("可用于后续映射 `material_id` 的候选字段包括：`creative_id`、`creative_name`、`note_id`、`image`、`jump_url`、`page_id`、`h5_material_info`、`creativity_extra_info`、`ad_biz_item_id`。这些字段只能作为候选，不在本 spike 修改 A 线素材契约。\n\n")

	b.WriteString("## 小红书与 Meta 字段模型主要差异\n\n")
	b.WriteString("| 主题 | 小红书聚光 | Meta 常见模型 | 影响 |\n")
	b.WriteString("|---|---|---|---|\n")
	b.WriteString("| 层级命名 | advertiser/campaign/unit/creativity | account/campaign/adset/ad/creative | `unit` 大致对应 Meta `adset`，但创意和广告对象边界不同。 |\n")
	b.WriteString("| 消费字段 | `fee` | `spend` | 需要指标命名映射。 |\n")
	b.WriteString("| 素材载体 | `note_id`、`image`、`jump_url`、组件字段 | creative asset、ad creative、object story 等 | 小红书笔记可能同时是内容资产和投放标的。 |\n")
	b.WriteString("| 转化字段 | 表单、私信、电商、外链、直播等平台语义较强 | standard/custom conversions | 需要按业务目标确认统一转化口径。 |\n")
	b.WriteString("| 关键词 | 关键词报表/关键词定向字段明显 | Meta 通常不是核心层级 | 搜索推广需要单独建模或作为扩展维度。 |\n\n")

	b.WriteString("## 仍需确认的问题\n\n")
	b.WriteString("- 业务同事/API 同事确认：当前 token 是否覆盖目标广告主、是否允许读取历史离线报表、是否有关键词报表权限。\n")
	b.WriteString("- 数据运营确认：小红书 `fee` 金额单位、时区、归因窗口、表单/有效表单/私信咨询等字段是否对应现有周报口径。\n")
	b.WriteString("- API 同事确认：`unit list` 的 `id` 与报表 `unit_id` 是否完全等价。\n")
	b.WriteString("- 业务同事确认：`note_id` 是否能稳定代表投放素材，程序化创意、多图/视频、落地页组件是否需要拆到素材变体。\n\n")

	b.WriteString("## Need Architecture Decision\n\n")
	b.WriteString("- 是否把小红书 `note_id` 纳入素材映射候选键，还是只作为平台创意属性保留。\n")
	b.WriteString("- 小红书 `creative_id` 与 `creativity_id` 命名差异进入统一契约时如何规范。\n")
	b.WriteString("- `unit` 是否在统一模型中映射为 `adset` 层，还是保留 channel-specific 层级名。\n")
	b.WriteString("- 创意图片 `creativity_image` / `image` 和跳转字段是否允许参与 `material_id` 半自动匹配。\n")
	b.WriteString("- 关键词层级是否进入第一版数据契约，还是作为搜索推广扩展事实表。\n\n")

	b.WriteString("## 下一步建议\n\n")
	if anyOK(report.Steps) {
		b.WriteString("建议进入下一步小红书 API 数据契约设计，但只限于 read-only 数据事实表和字段映射草案；素材映射契约变更需 Architecture 会话确认。\n")
	} else {
		b.WriteString("暂不建议进入正式数据契约设计。先补齐本地 `config/private/xhs/.env` 并跑通至少一个账号/列表/报表接口，再让 Architecture 会话判断映射设计。\n")
	}

	return os.WriteFile(path, []byte(b.String()), 0o644)
}

func classifyError(err error) string {
	msg := strings.ToLower(err.Error())
	var netErr net.Error
	switch {
	case errors.As(err, &netErr):
		return "网络或平台错误"
	case strings.Contains(msg, "json: cannot unmarshal"):
		return "接口字段未知"
	case strings.Contains(msg, "timeout") || strings.Contains(msg, "no such host") || strings.Contains(msg, "connection"):
		return "网络或平台错误"
	case strings.Contains(msg, "token") || strings.Contains(msg, "access"):
		return "token 无效"
	case strings.Contains(msg, "permission") || strings.Contains(msg, "unauthorized") || strings.Contains(msg, "forbidden") || strings.Contains(msg, "权限") || strings.Contains(msg, "无权"):
		return "advertiser_id 无权限"
	case strings.Contains(msg, "param") || strings.Contains(msg, "参数") || strings.Contains(msg, "required"):
		return "API 参数不完整"
	case strings.Contains(msg, "field") || strings.Contains(msg, "字段"):
		return "接口字段未知"
	default:
		return "平台返回错误"
	}
}

func sanitizeError(err error) string {
	msg := err.Error()
	for _, value := range redactionTokens {
		if value != "" {
			msg = strings.ReplaceAll(msg, value, maskToken(value))
		}
	}
	lower := strings.ToLower(msg)
	if idx := strings.Index(lower, "json: cannot unmarshal"); idx >= 0 {
		prefix := ""
		if colon := strings.Index(msg, ":"); colon > 0 && colon <= 4 {
			prefix = msg[:colon+1] + " response schema mismatch - "
		}
		return prefix + msg[idx:]
	}
	if len(msg) > 500 {
		return msg[:500] + "... [truncated]"
	}
	return msg
}

func tokenStatus(token string) string {
	if token == "" {
		return "missing"
	}
	return fmt.Sprintf("present length=%d", len(token))
}

func maskToken(token string) string {
	if token == "" {
		return ""
	}
	return fmt.Sprintf("[redacted length=%d]", len(token))
}

func redactID(id uint64) string {
	if id == 0 {
		return "missing"
	}
	raw := strconv.FormatUint(id, 10)
	if len(raw) <= 4 {
		return strings.Repeat("*", len(raw))
	}
	return raw[:2] + strings.Repeat("*", len(raw)-4) + raw[len(raw)-2:]
}

func parseUint(raw string) uint64 {
	v, _ := strconv.ParseUint(strings.TrimSpace(raw), 10, 64)
	return v
}

func firstNonEmpty(values ...string) string {
	for _, value := range values {
		if value != "" {
			return value
		}
	}
	return ""
}

func summarizeIDs(v any, kind string) any {
	b, err := json.Marshal(v)
	if err != nil {
		return map[string]string{"kind": kind}
	}
	var generic any
	if err := json.Unmarshal(b, &generic); err != nil {
		return map[string]string{"kind": kind}
	}
	return map[string]any{
		"kind":        kind,
		"schema_only": true,
		"json_fields": fieldNames(generic),
	}
}

func fieldNames(v any) []string {
	seen := map[string]bool{}
	var out []string
	var walk func(any)
	walk = func(x any) {
		switch typed := x.(type) {
		case map[string]any:
			for key, value := range typed {
				if !seen[key] {
					seen[key] = true
					out = append(out, key)
				}
				walk(value)
			}
		case []any:
			for _, item := range typed {
				walk(item)
			}
		default:
			_ = reflect.TypeOf(typed)
		}
	}
	walk(v)
	if len(out) > 40 {
		return out[:40]
	}
	return out
}

func hasFailures(steps []stepResult) bool {
	for _, step := range steps {
		if step.Status != "ok" {
			return true
		}
	}
	return false
}

func anyOK(steps []stepResult) bool {
	for _, step := range steps {
		if step.Status == "ok" {
			return true
		}
	}
	return false
}

func escapeMD(s string) string {
	s = strings.ReplaceAll(s, "\n", " ")
	s = strings.ReplaceAll(s, "|", "\\|")
	return s
}
