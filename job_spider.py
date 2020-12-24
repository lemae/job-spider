import jobui


class JobSpider:
    def __init__(self):
        print("\n欢迎使用JobSpider，所有职位信息来自职友集！")

    def __del__(self):
        pass

    def run(self):  # 实现主要逻辑
        while True:
            choice = self.get_choice()
            if choice == 'query':
                # 查询职位信息
                self.action_query()

            elif choice == 'exit':
                # 退出程序
                exit()

            else:
                print("无效的指令！")

    # 查询职位信息
    def action_query(self):
        print("查询职位信息，请输入有关参数：")
        job = input("职位名称（如'少儿编程'）：").strip()
        city = input("城市名称（如'广州'）：").strip()
        maxpagenum = int(input("最大爬取页数（0表示无限制）：").strip())
        print("\n")
        result = jobui.query(job, city, maxpagenum)
        print("\n")
        if result['state'] == 'success':
            print("统计信息（{}个职位）：".format(result['result']['quantity']))
            print("\n")
            print("\t职位：{} 城市：{}".format(job, city))
            print("\t" + "*" * 75 + "\n")  # 分隔符

            # 薪资
            print("\t\t\t\t\t薪资分析")
            salary = []
            salary.append(result['result']['salary']['avg'])
            salary.append(result['result']['salary']['0-5k'])
            salary.append(result['result']['salary']['5-10k'])
            salary.append(result['result']['salary']['10-20k'])
            salary.append(result['result']['salary']['20k+'])
            print("\t\t平均：{} 0-5k：{} 5-10k：{} 10-20k：{} 20k+：{}".format(salary[0], salary[1], salary[2], salary[3],
                                                                        salary[4]))
            # 学历
            print("\n\t\t\t\t\t最低学历")
            education = []
            education.append(result['result']['education']['大专'])
            education.append(result['result']['education']['本科'])
            education.append(result['result']['education']['硕士'])
            print("\t\t\t\t大专：{} 本科：{} 硕士：{}".format(education[0], education[1], education[2]))

            print("\n\t" + "*" * 75)  # 分隔符
            # 清洗率
            salary = result['result']['salary']['rate']
            education = result['result']['education']['rate']
            print("\t清洗率：薪资 {} 学历 {}".format(salary, education))
            print("\n")
        else:
            print("查询职位信息失败，错误信息：{} {}".format(result['error']['position'], result['error']['message']))
            print("\n")

    # 获得用户输入
    def get_choice(self):
        self.show_menu()
        choice = input("\t\t请输入指令：").strip()
        print("\n")
        return choice

    # 显示功能菜单
    def show_menu(self):
        print("\n\t\t\t\t功能菜单")
        print("\t\t" + "=" * 50 + "\n")

        # 功能列表
        print("\t\t\t    1. 查询职位信息 【 query 】")
        print("\t\t\t    2. 退出程序 【 exit 】")

        print("\n\t\t" + "=" * 50)
        print("\t\t\t    【】中的内容为指令\n")


job_spider = JobSpider()
job_spider.run()
