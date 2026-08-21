
# -*- encoding: utf-8 -*-
import copy
from globalConfig import Config
import base64


def append_section (str, key):
    return str + f"\n- {key}"

def append_property(str, key, value):
    return str + f"\n- {key}: {value}"

def format_keywords(keywords):
    index = 0
    keywords_str = ""
    for kw in keywords:
        if index >= Config.max_keyword_count:
            break
        if index > 0:
            keywords_str += ", "
        if kw['color']:
            keywords_str += f"<font color=\"{kw['color']}\">{kw['key']}</font>"
        else:
            keywords_str += kw['key']
        index += 1
    return keywords_str

'''飞书机器人的keywords格式化，因为忘存关键词的颜色了。。读取映射表还原意义也不大'''
def format_keywords_feishu(keywords):
    index = 0
    keywords_str = ""
    for kw in keywords:
        if index >= Config.max_keyword_count:
            break
        if index > 0:
            keywords_str += ", "
        keywords_str += kw
        index += 1
    return keywords_str

def format_resps(resps):
    output_resps = []
    index = 0
    for log in resps:
        if index >= Config.max_unique_resps:
            break
        resp = log.get("resp", {})
        guid = log.get("_guid_", "")
        seq = log.get("_seq_", "")
        lines = resp.split("\n")
        output_line = resp[:]
        if len(lines) > Config.max_per_resp_lines:
            output_line = "\n".join(lines[:Config.max_per_resp_lines])
        if len(output_line) > Config.max_per_resp_length:
            output_line = output_line[:Config.max_per_resp_length]
        output_resps.append({"guid": guid, "seq": seq, "resp": output_line})
        index += 1
    return output_resps

def get_cluster_card(timeRange,startTime,endTime,keyWords,resps,count,userCount,clusterChange,usersChange,isNew):
        # 处理keywords
    base = ""
    # 时间范围
    base = append_property(base, "<text_tag color='blue'>时间段</text_tag>", timeRange)
    # 关键词
    base = append_property(base, "<text_tag color='orange'>关键词</text_tag>",keyWords)
    # 时间段内数量
    base = append_property(base, "<text_tag color='blue'>时间段内数量</text_tag>", count)
    # 用户数量
    base = append_property(base, "<text_tag color='blue'>用户数量</text_tag>", userCount)
    if clusterChange > 0 :
        base = append_property(base, "<text_tag color='blue'>数量变化</text_tag>", clusterChange)
    if usersChange > 0 :
        base = append_property(base, "<text_tag color='blue'>用户变化</text_tag>", usersChange)
    if isNew:
        base = append_section(base, "<text_tag color='orange'>新增报错</text_tag>")
    data_success = copy.deepcopy(Config.data_success_template)
    data_success["card"]["elements"][0]["content"] = base
    # 部分报错
    # base = self.append_code(base, "部分报错", self.resps)
    if len(resps) > 0:
        panel = copy.deepcopy(Config.panel_template)
        index = 0
        result = ""
        for logInfo in resps:
            # 代码块
            # code_str = f"\n```lua\n{resp}\n```"
            if index > 0:
                # 换行符
                result += f"\n---\n"
            # 跳转查询具体报错
            resp = logInfo['resp']
            guid = logInfo['guid']
            seq = logInfo['seq']                
            result += resp
            if guid and seq:
                # 参数 开始时间,结束时间，query语句（base64加密）
                query = Config.query_template % (guid, seq)
                # 对query进行base64加密
                query = query.encode("utf-8")
                query = base64.b64encode(query)
                query = query.decode("utf-8")
                templateStr = Config.generate_query_url % (startTime, endTime, query)
                result += f"\n[查看详情]({templateStr})"
            # panel["elements"][0]["content"] += code_str
            index += 1
        panel["elements"][0]["content"] = result
        data_success["card"]["elements"].append(panel)
    return data_success
