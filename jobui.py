from parse_url import parse_url
from tqdm import tqdm, trange
from pprint import pprint
import time
import re
import json


# 职友集爬虫类
class JobuiSpider:
    position = "0000x0000"  # 错误处理机制，程序执行位置
    message = ''  # 错误处理机制，程序错误信息
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Mobile Safari/537.36"}
    re_totalpagenum = re.compile(r'pagination-last-link j-mobileTotalPageNum">(\d+)</span>')
    re_joblist = re.compile(
        r'<h3 class="job-name" title=".*?" data-positionID=".*?">(.*?)</h3>[\s|\S]*?<span class="f60 job-list-condition">(.*?)</span>[\s|\S]*?<span class="gray9 job-list-condition">(.*?)</span>[\s|\S]*?<span class="gray9 job-list-condition">(.*?)</span>[\s|\S]*?<span class="company-name" title=".*?">(.*?)</span>')

    def __int__(self):
        pass

    def __del__(self):
        pass

    # 错误处理机制，主动抛出异常
    def error(self, pos=None, mes=None):
        if pos != None: self.position = pos
        if mes != None: self.message = mes
        raise

    # 爬取指定页面，获取joblist
    # 模块：0001
    def _getjoblist(self, url):
        position = "0001x0001"

        joblist = list()  # 最终返回的结果
        # 爬取页面
        html_str = parse_url(url, headers=self.headers)
        # 提取数据
        result_list = self.re_joblist.findall(html_str)
        if result_list == []: self.error("0001x0002", "爬取失败，url：{}".format(url))
        result_list = result_list[:-1]
        # 生成job
        for result in result_list:
            job = dict()
            job['name'] = result[0]
            job['salary'] = result[1]
            job['experience'] = result[2]
            job['education'] = result[3]
            job['company'] = result[4]
            joblist.append(job)

        # 返回结果
        return joblist

    # 查询职位信息
    # 模块：0002
    def query(self, job, city, maxpagenum):
        position = "0002x0001"

        # 获取总页数
        job_url = "https://m.jobui.com/jobs?jobKw=" + job + "&cityKw=" + city
        html_str = parse_url(job_url, headers=self.headers)
        # print(html_str)
        totalpagenum = self.re_totalpagenum.search(html_str)
        if totalpagenum == None: self.error("0002x0002", "总页数获取失败")
        totalpagenum = int(totalpagenum.group(1))
        totalpagenum = maxpagenum if (maxpagenum != 0 and totalpagenum > maxpagenum) else totalpagenum

        # 生成待爬取的url列表
        url_list = [job_url + "&nowPage=" + str(i + 1) for i in range(totalpagenum)]

        result_dict = dict()  # 结果保存的字典
        issuccess = True  # 是否成功标志

        # 循环爬取全部数据
        print('本次需要爬取的页面共有' + str(totalpagenum) + '个')
        pbar = tqdm(list(range(totalpagenum)))
        for i in pbar:
            # 爬取joblist并保存在result_dict
            result = self._getjoblist(url_list[i])
            result_dict["第{}页".format(i + 1)] = result
            # 输出进度
            pbar.set_description("当前爬取进度：{}/{} 页".format(i + 1, totalpagenum))

        pbar.close()
        # 保存文件
        with open('result.json', 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)
            print("\n所需数据已经全部爬取成功，数据保存在result.json文件")

        # 对爬取到的数据进行处理，并返回结果
        return self._calculate_result_dict(result_dict)

    # 对爬取到的数据进行处理
    # 模块：003
    def _calculate_result_dict(self, result_dict):
        position = "0003x0001"

        # 总职位数
        quantity = 0
        for key in result_dict.keys():
            for job in result_dict[key]:
                quantity += 1

        # 处理薪资
        salary_dict = self._calculate_salary(result_dict)
        # salary_dict = {"avg":"9584元","0-5k":"5%","5-10k":"30%","10-20k":"35%","20k+":"30%",
        #             "rate": "76%"}

        # 处理学历
        education_dict = self._calculate_education(result_dict)
        # education_dict = {"大专": "20%", "本科": "20%", "硕士": "60%", "rate": "78%"}

        # 返回最终结果
        return {"quantity": quantity, "salary": salary_dict, "education": education_dict}

    # 处理薪资
    # 模块：004
    def _calculate_salary(self, result_dict):
        position = "0004x0001"

        salary_result = list()  # 最终薪资列表
        # 生成初始化薪资列表
        salary_initialize = list()
        for key in result_dict.keys():
            for job in result_dict[key]:
                salary_initialize.append(job['salary'])
        # 生成最终薪资列表
        for salary in salary_initialize:
            # 处理 千/月 与 万/月
            sign = salary[-3:]
            if sign == '千/月':
                ls = str(salary[:-3]).split("-")
                try:
                    min = float(ls[0]) * 1000
                    max = float(ls[1]) * 1000
                except:
                    continue
                salary_dict = {"min": min, "max": max}
                salary_result.append(salary_dict)
                continue
            elif sign == '万/月':
                ls = str(salary[:-3]).split("-")
                try:
                    min = float(ls[0]) * 10000
                    max = float(ls[1]) * 10000
                except:
                    continue
                salary_dict = {"min": min, "max": max}
                salary_result.append(salary_dict)
                continue

            # 处理 元
            sign = salary[-2:]
            if sign != '万元' and sign[-1:] == '元':  # 排除万元只处理元
                ls = str(salary[:-1]).split("-")
                try:
                    min = float(ls[0])
                    max = float(ls[1])
                except:
                    continue
                salary_dict = {"min": min, "max": max}
                salary_result.append(salary_dict)
                continue

            # 处理 K|k
            sign = salary[-1:]
            if sign == 'K' or sign == 'k':
                ls = str(salary[:-1]).split("-")
                try:
                    min = float(ls[0]) * 1000
                    max = float(ls[1]) * 1000
                except:
                    continue
                salary_dict = {"min": min, "max": max}
                salary_result.append(salary_dict)
                continue

        # 对最终薪资列表进行统计
        length = len(salary_result)  # 最终薪资列表长度
        len_0_5k = 0  # 0-5k
        len_5_10k = 0  # 5-10k
        len_10_20k = 0  # 10-20k
        len_20k_ = 0  # 20k+
        sum = 0  # 薪资和

        # 获取薪资分布
        for salary in salary_result:
            # 求和
            ls1 = (salary['min'] + salary['max']) / 2
            sum += ls1
            # 分布数量
            if ls1 < 5000: len_0_5k += 1
            if ls1 >= 5000 and ls1 < 10000: len_5_10k += 1
            if ls1 >= 10000 and ls1 < 20000: len_10_20k += 1
            if ls1 >= 20000: len_20k_ += 1

        # 分布概率
        if len_0_5k != 0: len_0_5k = int(round(len_0_5k / length, 2) * 100)  # 0-5k
        if len_5_10k != 0: len_5_10k = int(round(len_5_10k / length, 2) * 100)  # 5-10k
        if len_10_20k != 0: len_10_20k = int(round(len_10_20k / length, 2) * 100)  # 10-20k
        if len_20k_ != 0: len_20k_ = int(round(len_20k_ / length, 2) * 100)  # 20k+
        # print(len_0_5k, len_5_10k, len_10_20k, len_20k_)

        # 返回最终结果
        return {"avg": "{}元".format(int(sum / length)), "0-5k": "{}%".format(len_0_5k),
                "5-10k": "{}%".format(len_5_10k), "10-20k": "{}%".format(len_10_20k), "20k+": "{}%".format(len_20k_),
                "rate": "{}%".format(int(round(length / len(salary_initialize), 2) * 100))}

    # 处理学历
    # 模块：005
    def _calculate_education(self, result_dict):
        position = "0005x0001"

        education_result = list()  # 最终学历列表
        # 生成初始化学历列表
        education_initialize = list()
        for key in result_dict.keys():
            for job in result_dict[key]:
                education_initialize.append(job['education'])

        # 生成最终学历列表
        for education in education_initialize:
            if education.find('大专') != -1:
                education_result.append(education)
                continue
            if education.find('本科') != -1:
                education_result.append(education)
                continue
            if education.find('硕士') != -1:
                education_result.append(education)
                continue

        # 对最终学历列表进行统计
        length = len(education_result)  # 最终学历列表长度
        len_dz = 0  # 大专
        len_bk = 0  # 本科
        len_ss = 0  # 硕士

        # 学历分布数量
        for education in education_result:
            if education.find('大专') != -1: len_dz += 1
            if education.find('本科') != -1: len_bk += 1
            if education.find('硕士') != -1: len_ss += 1

        # 学历分布概率
        if len_dz != 0: len_dz = int(round(len_dz / length, 2) * 100)
        if len_bk != 0: len_bk = int(round(len_bk / length, 2) * 100)
        if len_ss != 0: len_ss = int(round(len_ss / length, 2) * 100)
        # print(len_dz, len_bk,len_ss)

        # 返回最终结果
        return {"大专": "{}%".format(len_dz), "本科": "{}%".format(len_bk), "硕士": "{}%".format(len_ss),
                "rate": "{}%".format(int(round(length / len(education_initialize), 2) * 100))}


jobui_spider = JobuiSpider()


# 查询职位信息
def query(job, city, maxpagenum):
    # result_dict = jobui_spider.query(job, city, maxpagenum)
    # return {'city': city, 'job': job, 'state': 'success', 'result': result_dict, 'error': None}
    try:
        result_dict = jobui_spider.query(job, city, maxpagenum)
        return {'city': city, 'job': job, 'state': 'success', 'result': result_dict, 'error': None}
    except:
        return {'city': city, 'job': job, 'state': 'failed', 'result': None,
                'error': {'position': jobui_spider.position, 'message': jobui_spider.message}}


if __name__ == '__main__':
    with open('result.json', 'r', encoding='utf-8') as f:
        jobui_spider._calculate_result_dict(json.load(f))
