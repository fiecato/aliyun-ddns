#!/usr/bin/env python
#coding=utf-8

# 加载核心SDK
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException

# 加载获取 、 新增、 更新、 删除接口
from aliyunsdkalidns.request.v20150109 import DescribeSubDomainRecordsRequest, AddDomainRecordRequest, UpdateDomainRecordRequest, DeleteDomainRecordRequest

# 加载内置模块
import json
import urllib

from common import loggings, config


logger = loggings.get_logger("ddns")


def getIp():
    """
    获取外网IP,三个地址返回的ip地址格式各不相同
        3322 的是最纯净的格式
        备选1 http://pv.sohu.com/cityjson?ie=utf-8 json格式 
        备选2 curl -L tool.lu/ip 为curl方式获取
    两个备选地址都需要对获取值作进一步处理才能使用
    """
    with urllib.request.urlopen('http://www.3322.org/dyndns/getip') as response:
        html = response.read()
        ip = str(html, encoding='utf-8').replace("\n", "")
    return ip


# 查询记录
def getDomainInfo(SubDomain, set_type="A"):
    request = DescribeSubDomainRecordsRequest.DescribeSubDomainRecordsRequest()
    request.set_accept_format('json')

    # 设置要查询的记录类型为 A记录   官网支持A / CNAME / MX / AAAA / TXT / NS / SRV / CAA / URL隐性（显性）转发  如果有需要可将该值配置为参数传入
    request.set_Type(set_type)

    # 指定查记的域名 格式为 'test.example.com'
    request.set_SubDomain(SubDomain)

    response = client.do_action_with_exception(request)
    response = str(response, encoding='utf-8')

    # 将获取到的记录转换成json对象并返回
    return json.loads(response)


# 新增记录 (默认都设置为A记录，通过配置set_Type可设置为其他记录)
def addDomainRecord(client, value, rr, domainname, set_type="A"):
    request = AddDomainRecordRequest.AddDomainRecordRequest()
    request.set_accept_format('json')

    # request.set_Priority('1')  # MX 记录时的必选参数
    request.set_TTL('600')       # 可选值的范围取决于你的阿里云账户等级，免费版为 600 - 86400 单位为秒 
    request.set_Value(value)     # 新增的 ip 地址
    request.set_Type(set_type)        # 记录类型
    request.set_RR(rr)           # 子域名名称  
    request.set_DomainName(domainname) #主域名

    # 获取记录信息，返回信息中包含 TotalCount 字段，表示获取到的记录条数
    # 0 表示没有记录， 其他数字为多少表示有多少条相同记录，正常有记录的值应该为1，如果值大于1则应该检查是不是重复添加了相同的记录
    response = client.do_action_with_exception(request)
    response = str(response, encoding='utf-8')
    relsult = json.loads(response)
    return relsult


# 更新记录
def updateDomainRecord(client,value,rr,record_id):
    request = UpdateDomainRecordRequest.UpdateDomainRecordRequest()
    request.set_accept_format('json')

    # request.set_Priority('1')
    request.set_TTL('600')
    request.set_Value(value) # 新的ip地址
    request.set_Type('A')
    request.set_RR(rr)
    request.set_RecordId(record_id)  # 更新记录需要指定 record_id ，该字段为记录的唯一标识，可以在获取方法的返回信息中得到该字段的值

    response = client.do_action_with_exception(request)
    response = str(response, encoding='utf-8')
    return response


# 删除记录
def delDomainRecord(client,subdomain):
    info = getDomainInfo(subdomain)
    if info['TotalCount'] == 0:
        logger.debug('没有相关的记录信息，删除失败！')
    elif info["TotalCount"] == 1:
        logger.debug('准备删除记录')
        request = DeleteDomainRecordRequest.DeleteDomainRecordRequest()
        request.set_accept_format('json')

        record_id = info["DomainRecords"]["Record"][0]["RecordId"]
        request.set_RecordId(record_id) # 删除记录需要指定 record_id ，该字段为记录的唯一标识，可以在获取方法的返回信息中得到该字段的值
        result = client.do_action_with_exception(request)
        logger.debug('删除成功，返回信息：{}'.format(result))
    else:
        # 正常不应该有多条相同的记录，如果存在这种情况，应该手动去网站检查核实是否有操作失误
        logger.debug("存在多个相同子域名解析记录值，请核查后再操作！")


def setDomainRecord(client, dynamicIP, subdomain, domainname):
    """
    有记录则更新，没有记录则新增
    """
    info = getDomainInfo(subdomain + '.' + domainname)
    if info['TotalCount'] == 0:
        logger.debug('准备添加新记录')
        add_result = addDomainRecord(client, dynamicIP, subdomain, domainname)
        logger.debug(add_result)
    elif info["TotalCount"] == 1:
        logger.debug('准备更新{}'.format(subdomain))
        record_id = info["DomainRecords"]["Record"][0]["RecordId"]
        old_ip = info["DomainRecords"]["Record"][0]["Value"]
        if dynamicIP == old_ip:
            logger.debug ("新ip: {}, 与原ip: {}, 相同，无需更新！".format(dynamicIP, old_ip))
        else:
            update_result = updateDomainRecord(client, dynamicIP, subdomain, record_id)
            logger.debug('更新成功，返回信息：{}'.format(update_result))
    else:
        # 正常不应该有多条相同的记录，如果存在这种情况，应该手动去网站检查核实是否有操作失误
        logger.debug("存在多个相同子域名解析记录值，请核查删除后再操作！")


if __name__ == "__main__":
    # 获取阿里云keyid和secret
    keyid = config.get("access", "keyid")
    secret = config.get("access", "secret")
    regionId = config.get("access", "regionId")

    DomainName = config.get("domain", "domain_name")
    SubDomainList = config.get_all("subdomain")

    # 配置认证信息
    client = AcsClient(keyid, secret, regionId)

    dynamicIP = getIp()

    for subdomain in SubDomainList:
        setDomainRecord(client, dynamicIP, subdomain, DomainName)

    # 删除记录测试
    # delDomainRecord(client,'b.jsoner.com')

    # 新增或更新记录测试
    # setDomainRecord(client,'192.168.3.222','a',DomainName)

    # 获取记录测试
    # logger.debug (getDomainInfo(DomainName, 'y'))

    # 批量获取记录测试
    # for x in SubDomainList:
    #     logger.debug (getDomainInfo(DomainName, x))

    # 获取外网ip地址测试
    # logger.debug ('(' + getIp() + ')')