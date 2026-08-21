import os
class Config:
    def __init__(self):
        pass
    
    @classmethod
    def reload_config_from_local(cls):
        try:
            with open("./Config.json", 'r', encoding='utf-8') as file:
                import json
                config_dict = json.load(file)
                
                # 更新匹配的类属性
                for key, value in config_dict.items():
                    if not key.startswith('__'):
                        setattr(cls, key, value)
        except FileNotFoundError:
            print(f"配置文件未找到。")
        except json.JSONDecodeError:
            print(f"配置文件格式错误。")
            
    # 数据库配置
    DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    DB_NAME = 'summary.db'
    DB_PATH = os.path.join(DB_DIR, DB_NAME)
    @classmethod
    def init_db_dir(cls):
        if not os.path.exists(cls.DB_DIR):
            os.makedirs(cls.DB_DIR)
            
    # endPoint
    endpoint = "us-east-1.log.aliyuncs.com"
    # project
    project = 'lw-client'#'lastwar-va'
    # logstore
    logStore = 'client'
    # access_key
    access_key_id = ''
    #access_key_secret
    access_key_secret = ''
    
    query = '''_level_ = Info
    and (
    "BundleUseIndex"
    )
    and (
    runtime: Android
    or runtime: iOS
    or runtime: Windows
    )
    and (
    store: com.fun.lastwar.gp
    or store: com.lastwar.ios
    or com.fun.lastwar.vn.gp
    or com.lastwar.pc
    or com.fun.lastwar.vn.ios
    )
    and (
    sid: APS1680
    or sid: APS1681
    or sid: APS1682
    )
    '''

    # 飞书机器人
    feishu_webhook = ''
    feishu_summary_webhook = ''
    
    method = "post"
    headers = {"Content-Type": "application/json"}

    titleContent = "报错统计"
    data_success_template = {
    "msg_type": "interactive",
    "card": {
        "config": {"enable_forward": True},
        "elements": [
            {
                "tag": "markdown",
                "content": '%s',
            },
            # {
            #     "actions": [
            #         {
            #             "tag": "button",
            #             "text": {
            #                 "content": btnContent,  # 这是卡片的按钮，点击可以跳转到url指向的allure路径
            #                 "tag": "lark_md",
            #             },
            #             "url": btnUrl,
            #             "type": "default",
            #             "value": {},
            #         }
            #     ],
            #     "tag": "action",
            # },
        ],
        # "header": {
        #     "title": {
        #         "content": titleContent,  # JOB_NAME 调用python定义的变量，这是卡片的标题
        #         "tag": "plain_text",
        #     },
        # },
    },
    }

    panel_template = {
        "tag": "collapsible_panel",
        "expanded": False,
        "header": {
            "title": {
                "tag": "plain_text",
                "content": "部分报错"
            },
            "vertical_align": "center",
            "icon": {
                "tag": "standard_icon",
                "token": "down-small-ccm_outlined",
                "color": "white",
                "size": "16px 16px"
            },
            "icon_position": "right",
            "icon_expanded_angle": -180
        },
        "border": {
            "color": "grey",
            "corner_radius": "5px"
        },
        "vertical_spacing": "8px",
        "padding": "8px 8px 8px 8px",
        "elements": [
            {
                "tag": "markdown",
                "content": ""
            }
        ]
    }

    # 时间段总结模板
    chart_pie_template = {
                    "tag": "chart",
                    "chart_spec": {
                        "type": "pie",
                        "title": {
                        "text": "占比"
                        },
                        "data": {
                        "values": '%s',
                        },
                        "valueField": "value",
                        "categoryField": "type",
                        "outerRadius": 0.9,
                        "innerRadius": 0.3,
                        "legends": {
                        "visible": True,
                        },
                        "label": {
                        "visible": True
                        }
                    }
                }
    
    
    chart_line_template = {
      "tag": "chart",
      "chart_spec": {
        "type": "line",
        "title": {
          "text": "趋势变化"
        },
        "data": {
          "values": '%s',
        },
        "xField": "time",
        "yField": "value"
      }
    }
    
    mark_down_template = {
                "tag": "markdown",
                "content": '%s',
            }
    
    # 聚类使用的正则
    # 先定义词组模式
    WORD_WITH_HYPHEN = r'[\w]+-[\w-]*[\w]+' # 带连字符的词组
    WORD_WITH_UNDERSCORE = r'[\w]+_[\w_]*[\w]+' # 带下划线的词组
    NORMAL_WORD = r'[\w]+' # 普通词组

    # 排除模式定义
    HEX_NUMBER = r'0x[0-9a-fA-F]+'          # 16进制数字
    PURE_NUMBER = r'\d+(?:-\d+)*\b'          # 纯数字(包括带连字符的数字)
    MD5_HASH = r'[0-9a-fA-F]{32}\b'         # 32位MD5哈希
    UUID = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b'  # UUID格式
    DELEGATE_METHOD = r'__gen_delegate_imp\d+'  # 委托方法
    DISPLAY_CLASS = r'c__displayclass\d+_\d+'   # 显示类
    BLOCK_CLASS = r'b__\d+_\d+'                 # 块类
    OTHER_GENERATED = r'd__\d+'                 # 其他生成的代码

    # 组合所有排除模式
    EXCLUDE_PATTERNS = f"(?:{HEX_NUMBER}|{PURE_NUMBER}|{MD5_HASH}|{UUID}|{DELEGATE_METHOD}|{DISPLAY_CLASS}|{BLOCK_CLASS}|{OTHER_GENERATED})"

    # 最终的正则表达式模式
    pattern = rf"""(?ux)    # 启用Unicode和详细模式
        \b                  # 词边界
        (?!{EXCLUDE_PATTERNS})  # 首先排除特殊格式
        (?:
            {WORD_WITH_HYPHEN}|   # 带连字符的词组
            {WORD_WITH_UNDERSCORE}| # 带下划线的词组
            {NORMAL_WORD}          # 普通词组
        )
        \b                 # 词边界
    """
    
    # max_df = 0.05
    # min_df = 1
    
    time_range = 1
    
    log_filter_words = [
        "Line breaking recursion max threshold hit",
        "roomData is nil roomId",
        '''MobileInput plugin OnData error: {"msg":"TEXT_CHANGE"''',
        '''#LoopList# SetVelocity异常!!!''',
        '''#LoopList# SetContainerLocalPosY异常''',
        "Material doesn't have a texture property '_MainTex'",
        "chatError 选择了不存在的房间",
        "SelectRoom is nil roomId",
        "InstanceRequest::ObjectPool cleared when request is still loading.",
        "协议收到 --------",
        "PveUnitGameObject HpText txt is not TextMeshProEx"
    ]
    
    keyword_url = ""
    generate_query_url = ""
    query_template = ''' _guid_ = %s and _seq_ = %s'''
    
    # increment_max_send_keywords = 300
    db_url = "sqlite:///./Data/keywords.db"
    archive_db_url = "sqlite:///./Data/archive.db"
    enable_output_cluster = True
    enable_output_summary = True
    enable_archive = True
    
    webhook_start_hour = 9
    webhook_end_hour = 22
    
    unique_id_name = "deviceId" # log中用于识别用户的字段名
    resp_id_name = "resp"   # log信息
    stackTrace_id_name = "stackTrace"   # log堆栈信息
    bundle_version = "packVer"  #log版本信息
    runtime_id = "runtime"
    
    tfidf_weight = 0.5
    textRank_weight = 0.5

    max_query_logs = 10