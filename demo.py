import streamlit as st
from datetime import datetime,date
import pandas as pd
import plotly_express as px
import time
import requests
import json
import re
from collections import deque
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(layout='wide')

# @st.cache_resource
def app(end_time_0,end_time_1,end_time_2,end_time_3,end_time_4):
    #st.set_page_config(layout='wide')
    
    def htrfundinfo(fundcode):
        '''
        fund_nav : DataFrame
            返回基金的净值日期（date）、单位净值（nav）、累计净值(cumnav)、净值回报率(equityReturn)、每份派送金(unitMoney).
        '''
        fund_id = fundcode
        history_tmurl="http://fund.eastmoney.com/pingzhongdata/"+fund_id+".js?v=20160518155842"
        #?v=20160518155842为时间戳，避免浏览器缓存
        print(fund_id)
        org_content = requests.get(history_tmurl)#向网站发起请求
        fund_info = org_content.text#获取网站返回的文本，即我们在浏览器中看到的全部文本数据
        temp_nav = re.findall(r"Data_netWorthTrend\s\=\s(\[\{.+\}\]);\/\*累计净值走势\*\/", fund_info)[0]#运用正则表达式，提取单位净值
        
        temp_nav = json.loads(temp_nav)#将文本数据，转化为字典格式
        temp_nav = pd.DataFrame(temp_nav)#将字典转化为dataframe格式
        temp_nav.rename(columns= {"x": "日期", "y":"净值"}, inplace=True)#修改列名称，x修改为date，y修改为nav
        #temp_nav = temp_nav.iloc[:20,:]
        n = len(temp_nav["日期"])
        # temp_nav["date"] = pd.to_datetime(temp_nav["date"])
        for i in range(n):
            temp_nav["日期"][i] = time.strftime('%Y-%m-%d',time.localtime(temp_nav["日期"][i]/1000.))#因为返回的时间是个时间戳，所以需要将其转化为正常的时间
        temp_nav=temp_nav.set_index('日期')#将时间设置为索引

        return temp_nav

    def htrfundinfo_time(start,end,code):
        fund_info = htrfundinfo(code).iloc[:,0:1]
        #选择爬下的净值个数
        fund_info_time = fund_info[start:end]
        return fund_info_time

    def merge_price(type, name=''):
        df_2= pd.read_excel(r'.\demo.xlsx',sheet_name='名单')
        df_3= pd.read_excel(r'.\demo.xlsx',sheet_name='净值')
        # df_3 = df_3.set_index('日期')
        #merge_table = df_3
        if type == '全部':
            df_2_gongmu = df_2[df_2['公私募']=='公募']

            name_list = []
            i = 0
            for row in df_2_gongmu.itertuples():
                i+=1
                name = getattr(row,'产品')
                #选择起止时间，按产品编号遍历
                code = str(name).split("(")[1].split(")")[0]
                print(code)
                df_api_value = htrfundinfo_time('2020','2024',str(code))
                #name = getattr(row,'产品')

                df_api_value = df_api_value.rename(columns={'净值':name})
                name_list.append(name)
                if i == 1:
                    df_api_value_all = df_api_value
                else:
                    df_api_value_all[name] = df_api_value[name]

            df_api_value_all.index= df_api_value_all.index.astype(str)
            df_3['日期'] = pd.to_datetime(df_3['日期']).dt.strftime('%Y-%m-%d')

            merge_table = pd.concat([df_3.set_index('日期'), df_api_value_all], axis=1, sort=True)
            merge_table.fillna("", inplace=True)
            merge_table.reset_index(inplace=True,drop=False)
            merge_table['日期'] = pd.to_datetime(merge_table['日期'])
            return merge_table
        elif type == '公募':
            df_2_gongmu = df_2[df_2['公私募']=='公募']

            name_list = []
            i = 0
            for row in df_2_gongmu.itertuples():
                i+=1
                name = getattr(row,'产品')
                #选择起止时间，按产品编号遍历
                code = str(name).split("(")[1].split(")")[0]
                print(code)
                df_api_value = htrfundinfo_time('2020','2024',str(code))
                #name = getattr(row,'产品')

                df_api_value = df_api_value.rename(columns={'净值':name})
                name_list.append(name)
                if i == 1:
                    df_api_value_all = df_api_value
                else:
                    df_api_value_all[name] = df_api_value[name]

            df_api_value_all.index= df_api_value_all.index.astype(str)
            #df_3['日期'] = pd.to_datetime(df_3['日期']).dt.strftime('%Y-%m-%d')

            #merge_table = pd.concat([df_3.set_index('日期'), df_api_value_all], axis=1, sort=True)
            df_api_value_all.fillna(1, inplace=True)
            df_api_value_all.reset_index(inplace=True,drop=False)
            df_api_value_all['日期'] = pd.to_datetime(df_api_value_all['日期'])
            return df_api_value_all
        elif type == '私募':
            return df_3

    def show_chart(type):
        print("------------------------------------------------")
        print("------------------------------------------------")
        print("------------------------------------------------")
        
        print("------------------------------------------------")
        print("------------------------------------------------")
        print("------------------------------------------------")
        df_flow= pd.read_excel(r'.\demo.xlsx',sheet_name='买卖',usecols=['产品','操作时间','操作方向','操作金额','操作份额'])
        df_price_original= pd.read_excel(r'.\demo.xlsx',sheet_name='净值')
        df_name= pd.read_excel(r'.\demo.xlsx',sheet_name='名单')
        df_price=merge_price('全部')
        #df_price.to_csv('1.csv', index=False)
        
        #将产品名称写入name
        df_li = df_name.values.tolist()
        name = []
        name_map = {}

        for s_li in df_li:
            if (s_li[3] == type or type == '全部'):
                name.append(s_li[1])
                name_map[s_li[1]] = s_li
        #print(name_map)
        
        print("################################################")
        print("#############	CURRENT  	   ################")
        print("################################################")
        hold_amount_list = [] #持有数量列表
        hold_money_list = [] #持有金额列表
        alive_list = [] #保有情况列表
        last_alive_list = []
        
        #本金
        money_cost_list = []
        last_money_cost_list = []
        
        #收益
        hold_profit_list = [] 
        sold_profit_list = []
        total_profit_list = []
        
        #价格
        cost_price_list = []
        last_price_list = []
    
        #当年买入卖出
        current_buy_alive_list = [] #当年买入情况
        current_sell_alive_list = [] #当年卖出情况
        current_buy_money_list = []
        current_sell_money_cost_list = []
        
        start_year_time =pd.Timestamp("2022-12-25 00:00:00")
        for row in name:
            cost_pirce = 0
            hold_amount = 0
            hold_profit = 0
            sold_profit = 0
            buy_money = 0
            sell_money_cost = 0 #卖出本金
            current_buy_amount = 0
            current_sell_amount = 0
            current_buy_money = 0
            current_sell_money_cost = 0 #本年卖出本金
            last_buy_money = 0
            last_sell_money_cost = 0 #历史卖出本金
            flow = df_flow[(df_flow['产品'].isin([row]))]
            print("------------"+row+"------------")
            flow_list = flow.values.tolist()
            for one_flow in flow_list:
                print(one_flow[1], one_flow[2], one_flow[3])
                price = df_price[(df_price['日期'].isin([one_flow[1]]))][row].values.tolist()[0]
                print(price)
                if one_flow[2] == '申购买入':
                    cost_pirce = (cost_pirce * hold_amount + one_flow[3]) / (hold_amount + one_flow[4])   
                    hold_amount = hold_amount + one_flow[4]
                    buy_money = buy_money + one_flow[3]
                    if one_flow[1] > start_year_time:
                        current_buy_amount = current_buy_amount + one_flow[4]
                        current_buy_money = current_buy_money + one_flow[3]
                    else:
                        last_buy_money = last_buy_money + one_flow[3]
                elif one_flow[2] == '认购买入':
                    price = 1
                    cost_pirce = (cost_pirce * hold_amount + one_flow[3]) / (hold_amount + one_flow[4])
                    hold_amount = hold_amount + one_flow[4]
                    buy_money = buy_money + one_flow[3]
                    if one_flow[1] > start_year_time:
                        current_buy_amount = current_buy_amount + one_flow[4]
                        current_buy_money = current_buy_money + one_flow[3]
                    else:
                        last_buy_money = last_buy_money + one_flow[3]
                elif one_flow[2] == '赎回卖出':
                    sold_profit = sold_profit + one_flow[3] - cost_pirce * one_flow[4]
                    sell_money_cost = sell_money_cost + cost_pirce * one_flow[4]
                    if (hold_amount - one_flow[4]) < 5 and (hold_amount - one_flow[4]) > -5:
                        hold_amount = 0
                    else:
                        hold_amount = hold_amount - one_flow[4]
                    if one_flow[1] > start_year_time:
                        current_sell_amount = current_sell_amount + one_flow[4]
                        current_sell_money_cost = current_sell_money_cost + cost_pirce * one_flow[4] #本年卖出本金累计
                    else:
                        last_sell_money_cost = last_sell_money_cost + cost_pirce * one_flow[4]
                elif one_flow[2] == '现金分红':
                    sold_profit = sold_profit + one_flow[3]
                    #sell_money = sell_money + one_flow[3]
                elif one_flow[2] == '份额分红':
                    cost_pirce = cost_pirce * hold_amount  / (hold_amount + one_flow[4])
                    hold_amount = hold_amount + one_flow[4]
                    #sold_profit = sold_profit + one_flow[4] * (price - cost)  
            last_price = 0
            for one_price in df_price[row].values.tolist():
                if one_price:
                    last_price = one_price
            print('last', last_price)
            hold_profit = (last_price - cost_pirce) * hold_amount
            hold_amount_list.append(round(hold_amount))
            hold_money_list.append(round(hold_amount * last_price))
            hold_profit_list.append(round(hold_profit))
            sold_profit_list.append(round(sold_profit))
            total_profit_list.append(round(hold_profit+ sold_profit))
            cost_price_list.append(cost_pirce)
            last_price_list.append(last_price)
            #buy_money_list.append(buy_money)
            #sell_money_list.append(sell_money)
            if round(hold_amount) == 0:
                alive_list.append(0)
            else:
                alive_list.append(1)
            if (hold_amount - (current_buy_amount- current_sell_amount) > 5):
                last_alive_list.append(1)
            else:
                last_alive_list.append(0)
            if (hold_amount - (current_buy_amount- current_sell_amount) < 5) and (current_buy_amount != 0):
                current_buy_alive_list.append(1)
            else:
                current_buy_alive_list.append(0)
            if (hold_amount  < 5) and (current_sell_amount != 0):
                current_sell_alive_list.append(1)
            else:
                current_sell_alive_list.append(0)
            current_buy_money_list.append(current_buy_money)
            current_sell_money_cost_list.append(current_sell_money_cost)  
            money_cost_list.append(buy_money-sell_money_cost)
            last_money_cost_list.append(last_buy_money-last_sell_money_cost)
            #if round(hold_amount * last_price - (current_buy_money - current_sell_money)) > 0:
                
                
        df_name = df_name[(df_name['产品'].isin(name))]
        df_name['成本价']=cost_price_list 
        df_name['当前净值']=last_price_list
        df_name['持有数量']=hold_amount_list
        
        #df_name['投资总金额']=buy_list 
        #df_name['卖出总金额']=sell_list
        #df_name['持有金额']=hold_list 
        
        df_name['产品数量合计']=alive_list
        df_name['上年结转']=last_alive_list
        df_name['本年新投']=current_buy_alive_list
        df_name['本年赎回']=current_sell_alive_list
            
        df_name['投资原始成本']=money_cost_list
        df_name['上年结转(本金)']=last_money_cost_list
        df_name['本年新投(本金)']=current_buy_money_list
        df_name['本年赎回(本金)']=current_sell_money_cost_list
        
        df_name['投资总金额']=hold_money_list
        
        df_name['当前持有收益']=hold_profit_list   
        df_name['当前了结收益']=sold_profit_list   
        df_name['当前汇总收益']=total_profit_list

        #col1, col2, col3 = st.columns(3)
        #col1.metric("持有总金额", round(sum(hold_list),2), "", delta_color="inverse")
        #col2.metric("汇总收益", round(sum(total_profit_list),2), "", delta_color="inverse")
        #col3.metric("持有数量", len(name), "", delta_color="inverse")
        
        last_time_list = {}
        for row in name:
            #continue
            one_row_last_time_list = []
            
            time_list = df_price['日期']
            #end_time_0 =pd.Timestamp("2023-04-16 00:00:00")
            #last_time_0 =pd.Timestamp("2023-04-16 00:00:00")
            
            # end_time_1 =pd.Timestamp("2023-04-01 00:00:00")
            # last_time_1 =pd.Timestamp("2023-04-01 00:00:00")
            
            #end_time_2 =pd.Timestamp("2022-12-25 00:00:00")
            #last_time_2 =pd.Timestamp("2022-12-25 00:00:00")
            
            # end_time_3 =pd.Timestamp("2021-12-25 00:00:00")
            # last_time_3 =pd.Timestamp("2021-12-25 00:00:00")
            
            # end_time_4 =pd.Timestamp("2020-12-25 00:00:00")
            # last_time_4 =pd.Timestamp("2020-12-25 00:00:00")
            
            for one_time in time_list:	
                one_price = df_price[(df_price['日期'].isin([one_time]))][row].values.tolist()[0]
                if (one_time < end_time_0):
                    #one_price = df_price[(df_price['日期'].isin([one_time]))][row].values.tolist()[0]
                    if one_price:
                        last_time_0 = one_time
                if (one_time < end_time_1):
                    #one_price = df_price[(df_price['日期'].isin([one_time]))][row].values.tolist()[0]
                    if one_price:
                        last_time_1 = one_time
                if (one_time < end_time_2):
                    #one_price = df_price[(df_price['日期'].isin([one_time]))][row].values.tolist()[0]
                    if one_price:
                        last_time_2 = one_time
                if (one_time < end_time_3):
                    #one_price = df_price[(df_price['日期'].isin([one_time]))][row].values.tolist()[0]
                    if one_price:
                        last_time_3 = one_time
                if (one_time < end_time_4):
                    #one_price = df_price[(df_price['日期'].isin([one_time]))][row].values.tolist()[0]
                    if one_price:
                        last_time_4 = one_time
            #print(last_time, df_price[(df_price['日期'].isin([last_time]))][row])
            one_row_last_time_list.append(last_time_0)
            one_row_last_time_list.append(last_time_1)
            one_row_last_time_list.append(last_time_2)
            one_row_last_time_list.append(last_time_3)
            one_row_last_time_list.append(last_time_4)
            
            last_time_list[row] = one_row_last_time_list

        for last_time_index in range(5):
            amount_list = []
            hold_money_list_last = []
            hold_money_list_current = []
            cost_list = []
            last_price_list = []
            
            hold_profit_list = []
            sold_profit_list_last = []
            sold_profit_list_current = []
            
            total_profit_list_last = []
            total_profit_list_current = []
            total_profit_list_current_pos = []
            total_profit_list_current_pos_amount = []
            total_profit_list_current_neg = []
            total_profit_list_current_neg_amount = []
            for row in name:
                print("################################################")
                print(last_time_list[row][last_time_index])
                print("################################################")
                cost = 0
                amount = 0
                hold_profit = 0
                sold_profit = 0
                buy = 0
                sell = 0
                flow = df_flow[(df_flow['产品'].isin([row]))]
                print("------------"+row+"------------")
                flow_list = flow.values.tolist()
                last_time = last_time_list[row][last_time_index]
                print(last_time, df_price[(df_price['日期'].isin([last_time]))][row])
                for one_flow in flow_list:
                    if (one_flow[1] > last_time):
                        continue
                    print(one_flow[1], one_flow[2], one_flow[3])
                    price = df_price[(df_price['日期'].isin([one_flow[1]]))][row].values.tolist()[0]
                    print(price)
                    if one_flow[2] == '申购买入':
                        cost = (cost * amount + one_flow[3]) / (amount + one_flow[4])   
                        amount = amount + one_flow[4]
                        buy = buy + one_flow[3]
                    elif one_flow[2] == '认购买入':
                        price = 1
                        cost = (cost * amount + one_flow[3]) / (amount + one_flow[4])
                        amount = amount + one_flow[4]
                        buy = buy + one_flow[3]
                    elif one_flow[2] == '赎回卖出':
                        sold_profit = sold_profit + one_flow[3] - cost * one_flow[4]
                        sell = sell + one_flow[3]
                        if (amount - one_flow[4]) < 5 and (amount - one_flow[4]) > -5:
                            amount = 0
                        else:
                            amount = amount - one_flow[4]
                    elif one_flow[2] == '现金分红':
                        sold_profit = sold_profit + one_flow[3]
                        sell = sell + one_flow[3]
                    elif one_flow[2] == '份额分红':
                        cost = cost * amount  / (amount + one_flow[4])
                        amount = amount + one_flow[4]
                        
                #######
                if len(df_price[(df_price['日期'].isin([last_time]))][row].values.tolist()) != 0:
                    last_price = df_price[(df_price['日期'].isin([last_time]))][row].values.tolist()[0]
                    if last_price:
                        last_price = last_price
                    else:
                        last_price = 0
                else:
                    last_price = 0
                #######
                print('last', last_time, last_price)
                hold_profit = (last_price - cost) * amount
                amount_list.append(round(amount))
                hold_money_list_last.append(round(amount * last_price))
                hold_profit_list.append(round(hold_profit))
                sold_profit_list_last.append(round(sold_profit))
                total_profit_list_last.append(round(hold_profit+ sold_profit))
                index = len(total_profit_list_last) - 1
                total_profit_list_current.append(total_profit_list[index] - total_profit_list_last[index])
                sold_profit_list_current.append(sold_profit_list[index] - sold_profit_list_last[index])
                hold_money_list_current.append(hold_money_list[index] - hold_money_list_last[index])
                if total_profit_list_current[index] > 0:
                    total_profit_list_current_pos.append(1)
                    total_profit_list_current_pos_amount.append(total_profit_list_current[index])
                    total_profit_list_current_neg.append(0)
                    total_profit_list_current_neg_amount.append(0)
                elif total_profit_list_current[index] < 0:
                    total_profit_list_current_pos.append(0)
                    total_profit_list_current_pos_amount.append(0)
                    total_profit_list_current_neg.append(1)
                    total_profit_list_current_neg_amount.append(-total_profit_list_current[index])
                else:
                    total_profit_list_current_pos.append(0)
                    total_profit_list_current_pos_amount.append(0)
                    total_profit_list_current_neg.append(0)
                    total_profit_list_current_neg_amount.append(0)
                cost_list.append(cost)
                last_price_list.append(last_price)

            if last_time_index == 0:
                df_name['本周盈亏']=total_profit_list_current
                df_name['本周浮盈数量']=total_profit_list_current_pos
                df_name['本周浮盈金额']=total_profit_list_current_pos_amount
                df_name['本周浮亏数量']=total_profit_list_current_neg
                df_name['本周浮亏金额']=total_profit_list_current_neg_amount 	
                df_name['赎回到账盈亏金额周']=sold_profit_list_current
            elif last_time_index == 1:
                df_name['本月盈亏']=total_profit_list_current
                df_name['本月浮盈数量']=total_profit_list_current_pos
                df_name['本月浮盈金额']=total_profit_list_current_pos_amount
                df_name['本月浮亏数量']=total_profit_list_current_neg
                df_name['本月浮亏金额']=total_profit_list_current_neg_amount 
                df_name['上月盈亏']=total_profit_list_last
                df_name['赎回到账盈亏金额月']=sold_profit_list_current
            elif last_time_index == 2:
                df_name['本年盈亏']=total_profit_list_current
                df_name['本年浮盈数量']=total_profit_list_current_pos
                df_name['本年浮盈金额']=total_profit_list_current_pos_amount
                df_name['本年浮亏数量']=total_profit_list_current_neg
                df_name['本年浮亏金额']=total_profit_list_current_neg_amount			
                df_name['上年盈亏']=total_profit_list_last
                df_name['赎回到账盈亏金额年']=sold_profit_list_current
                
                df_name['上年结转(净值)']=hold_money_list_last
                df_name['本年净新增']=hold_money_list_current
                    
                df_name['2022年持有收益']=hold_profit_list
                df_name['2022年了结收益']=sold_profit_list_last
                df_name['2022年汇总收益']=total_profit_list_last
            elif last_time_index == 3:
                df_name['2021年持有收益']=hold_profit_list
                df_name['2021年了结收益']=sold_profit_list_last
                df_name['2021年汇总收益']=total_profit_list_last
            elif last_time_index == 4:
                df_name['2020年持有收益']=hold_profit_list
                df_name['2020年了结收益']=sold_profit_list_last
                df_name['2020年汇总收益']=total_profit_list_last
        
        return df_name
        
    def summary():
        df_1= pd.read_excel(r'.\summary.xlsx',sheet_name='产品')
        df_2= pd.read_excel(r'.\demo.xlsx',sheet_name='名单')

        type = df_2['投资产品类型'].unique()
        df_1.insert(loc=0, column='投资产品类型', value=type)
        df_1 = pd.DataFrame(df_1).set_index('投资产品类型')
        return df_1

    if 'df_name' not in st.session_state:
        df_name = show_chart(type='全部')
        st.session_state.df_name = df_name

    model_1=st.sidebar.radio('投资统计',('总体情况','产品类型','单项产品','产品比对')) 
    if model_1 == '总体情况':
        if st.sidebar.button("更新数据"):
            df_name = show_chart(type='全部')
            st.session_state.df_name = df_name
        df_name = st.session_state.df_name
        model_2=st.sidebar.radio('统计维度',('产品','资金','年度','月度','周度')) 
        st.subheader('总体情况——'+model_2)
        df_all = summary()
        class_product = ['产品数量合计','上年结转','本年新投','本年赎回']
        class_finace = ['投资原始成本','上年结转(本金)','本年新投(本金)','本年赎回(本金)']
        class_invest = ['投资总金额','上年结转(净值)','本年净新增']
        class_year = ['本年盈亏','本年浮盈数量','本年浮盈金额','本年浮亏数量','本年浮亏金额','赎回到账盈亏金额年','上年盈亏']
        class_month = ['本月盈亏','本月浮盈数量','本月浮盈金额','本月浮亏数量','本月浮亏金额','赎回到账盈亏金额月','上月盈亏']
        class_week = ['本周盈亏','本周浮盈数量','本周浮盈金额','本周浮亏数量','本周浮亏金额','赎回到账盈亏金额周']
        
        class_money = class_finace+ class_invest
        
        class_all = class_product+ class_money+ class_year+ class_month+ class_week
        
        for one_class in class_all:
            df_all[one_class] = df_name.groupby(['投资产品类型'])[one_class].sum()
        
        #绘制饼图
        def pie(df_all_new):
            col1, col2 = st.columns([1, 1])
            with col1:
                st.dataframe(data=df_all_new,width=1500,height=700)
                
            with col2:
                plt.rcParams['font.family'] = ['Microsoft YaHei']
                option = st.selectbox('请选择要显示的内容：', df_all_new.columns)
                #将小于0的数据设置为0
                df_all_new.loc[df_all_new[option] < 0, option] = 0
                values = df_all_new[option].values
                labels = df_all_new.index.values
                
                if np.sum(values) == 0:
                    st.error('此项没有进行任何产品投资，请重新选择！')
                else:
                    # 绘制相应的饼图
                    fig, ax = plt.subplots(figsize=(6, 6))
                    ax.pie(values, labels=labels, autopct='%1.1f%%')

                    # 显示饼图
                    st.pyplot(fig)

        if model_2 == '产品':
            df_all_new = df_all.drop(columns=class_money+ class_year+ class_month+ class_week,axis=1)
            #df_all_new = pd.DataFrame(df_all_new[1:], columns=df_all_new[0])
            pie(df_all_new)
        elif model_2 == '资金':
            df_all_new = df_all.drop(columns=class_product+ class_year+ class_month+ class_week,axis=1)
            pie(df_all_new)
            #st.dataframe(data=df_all_new,width=1500,height=400)
        elif model_2 == '年度':
            df_all_new = df_all.drop(columns=class_product+ class_money+ class_month+ class_week,axis=1)
            # st.dataframe(data=df_all_new,width=1500,height=400)
            pie(df_all_new)
        elif model_2 == '月度':
            df_all_new = df_all.drop(columns=class_product+ class_money+ class_year+ class_week,axis=1)
            # st.dataframe(data=df_all_new,width=1500,height=400)
            pie(df_all_new)
        elif model_2 == '周度':
            df_all_new = df_all.drop(columns=class_product+ class_money+ class_year+ class_month,axis=1)
            # st.dataframe(data=df_all_new,width=1500,height=400)
            pie(df_all_new)
        class_1 = []
        class_2 = []
        for one_class in class_product:
            class_2.append(one_class)
            class_1.append('产品汇总')
        for one_class in class_money:
            class_2.append(one_class)
            class_1.append('资金情况')
        for one_class in class_year:
            class_2.append(one_class)
            class_1.append('年度收益')
        for one_class in class_month:
            class_2.append(one_class)
            class_1.append('月度收益')
        for one_class in class_week:
            class_2.append(one_class)
            class_1.append('周度收益')
        df_all.columns = pd.MultiIndex.from_arrays([class_1,class_2])
        
        df_2= pd.read_excel(r'.\demo.xlsx',sheet_name='名单')
        type_list = df_2['投资产品类型'].unique()
        class_1 = []
        class_2 = []
        for one_type in type_list:
            class_2.append(one_type)
            class_1.append(df_2[(df_2['投资产品类型'].isin([one_type]))]['公私募'].values.tolist()[0])
        df_all.index = pd.MultiIndex.from_arrays([class_1,class_2])
        #st.dataframe(data=df_all,width=1500,height=400)
        df_all.to_excel('all.xlsx', index=True)
        with open('all.xlsx', 'rb') as my_file:
            st.sidebar.download_button(label = '下载表格', data = my_file, file_name = '汇总.xlsx', mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')  
    elif model_1 == '产品类型':
        if st.sidebar.button("更新数据"):
            df_name = show_chart(type='全部')
            st.session_state.df_name = df_name
        df_name = st.session_state.df_name
        st.subheader('产品类型')
        df_2= pd.read_excel(r'.\demo.xlsx',sheet_name='名单')
        type_list = df_2['投资产品类型'].unique()
        model_2=st.sidebar.radio('产品类型',type_list) 
        st.subheader(model_2)
        col1,col2,col3=st.columns(3)
        with col1:
            part1=st.checkbox('2022年度')
        with col2:
            part2=st.checkbox('2021年度')
        with col3:
            part3=st.checkbox('2020年度') 
        #df_name = show_chart(type=model_2, need2022=part1, need2021=part2, need2020=part3)
        df_name_new = df_name[(df_name['投资产品类型'].isin([model_2]))]
        #df_name_new = df_name_new.drop(columns=['公私募','投资产品类型', '目前产品数量','本年新投','本年赎回','本周浮盈数量','本周浮亏数量','本月浮盈产品数量','本月浮亏产品数量','本年浮盈产品数量','本年浮亏产品数量','上年结转','本月浮盈浮亏','本年累计浮盈'],axis=1)
        if not part1:
            df_name_new = df_name_new.drop(columns=['2022年持有收益','2022年了结收益', '2022年汇总收益'],axis=1)
        if not part2:
            df_name_new = df_name_new.drop(columns=['2021年持有收益','2021年了结收益', '2021年汇总收益'],axis=1)
        if not part3:
            df_name_new = df_name_new.drop(columns=['2020年持有收益','2020年了结收益', '2020年汇总收益'],axis=1)
        #df_name.drop(columns=['公私募','投资产品类型', '持有情况','当年买入','当年赎回','当年买入金额','当年赎回金额'],axis=1,inplace=True) 
        #df_name.drop(columns=['2022年持有情况','2022年持有金额'],axis=1,inplace=True)
        df_name_new.set_index(['产品'],inplace=True)
        st.dataframe(data=df_name_new,width=1500,height=400)
    elif model_1 == '单项产品':
        st.subheader('单项产品')
        
        df_name_new= pd.read_excel(r'.\demo.xlsx',sheet_name='名单')
        starselect_1=st.selectbox('选择产品',df_name_new['产品']) 
        df_flow= pd.read_excel(r'.\demo.xlsx',sheet_name='买卖',usecols=['产品','操作时间','操作方向','操作金额','操作份额'])
        flow = df_flow[(df_flow['产品'].isin([starselect_1]))]
        
        name = df_name_new[(df_name_new['产品'].isin([starselect_1]))]
        df_price=merge_price('私募')
        if name['公私募'].values.tolist()[0] == '公募':
            df_price=merge_price('公募')
        elif name['公私募'].values.tolist()[0] == '私募':
            df_price=merge_price('私募')
        
        cost = 0
        amount = 0
        hold_profit = 0
        sold_profit = 0 
        buy = 0
        sell = 0
        price_list = []
        cost_list = []
        amount_list = []
        hold_amount_list = []
        hold_profit_list = []
        sold_profit_list = []
        #print(flow)
        flow_list = flow.values.tolist()
        buy_deque = deque()
        for one_flow in flow_list:
            print(one_flow)
            price = df_price[(df_price['日期'].isin([one_flow[1]]))][starselect_1].values.tolist()[0]
            if one_flow[2] == '申购买入':
                #if name['公私募'].values.tolist()[0] == '公募':
                #	if one_flow[3] < 1000000:
                #		one_flow[3] = one_flow[3] / (1+0.0012)
                #	elif one_flow[3] < 3000000:
                #		one_flow[3] = one_flow[3] / (1+0.0008)
                #	elif one_flow[3] < 5000000:
                #		one_flow[3] = one_flow[3] / (1+0.0003)
                #	else:
                #		one_flow[3] = one_flow[3] - 1000
                #elif name['公私募'].values.tolist()[0] == '私募':
                #	one_flow[3] = one_flow[3] * 0.9998
                cost = (cost * amount + one_flow[3]) / (amount + one_flow[4])   
                amount = amount + one_flow[4]
                buy = buy + one_flow[3]
                amount_list.append(one_flow[4])
                #one_flow[4] = round(one_flow[3]/ price)
                buy_deque.append(one_flow)
            elif one_flow[2] == '认购买入':
                price = 1
                cost = (cost * amount + one_flow[3]) / (amount + one_flow[3]/ price)
                amount = amount + one_flow[3]/ price
                buy = buy + one_flow[3]
                amount_list.append(round(one_flow[3]/ price))
            elif one_flow[2] == '赎回卖出':
                sold_profit = sold_profit + one_flow[3] - cost * one_flow[4]
                sell = sell + one_flow[3]
                
                #temp_amount = one_flow[4]
                #print(buy_deque)  
                #while(temp_amount > 5):
                    #print(temp_amount)
                    #temp_flow = buy_deque.popleft()
                    #if temp_flow[4] - temp_amount > 1:
                    #	temp_flow[4] = temp_flow[4] - temp_amount 
                    #	buy_deque.appendleft(temp_flow)
                    #	temp_amount = 0 
                    #else:
                    #	temp_amount = temp_amount - temp_flow[4]
                    #print(temp_flow[1], one_flow[1])
                    #print(buy_deque)				
                
                if (amount - one_flow[4]) < 5 and (amount - one_flow[4]) > -5:
                    amount = 0
                else:
                    amount = amount - one_flow[4]
                amount_list.append(one_flow[4])
            elif one_flow[2] == '现金分红':
                sold_profit = sold_profit + one_flow[3]
                sell = sell + one_flow[3]
                amount_list.append(0)
            elif one_flow[2] == '份额分红':
                cost = cost * amount  / (amount + one_flow[4])
                amount = amount + one_flow[4]
                amount_list.append(one_flow[4])
                buy_deque.append(one_flow)
            price_list.append(price)
            hold_amount_list.append(round(amount))
            cost_list.append(cost)
        #flow['操作份额计'] = amount_list
        flow['累计份额'] = hold_amount_list
        flow['操作净值'] = price_list
        flow['成本价'] = cost_list
        last_price = 0
        for one_price in df_price[starselect_1].values.tolist():
            if one_price:
                last_price = one_price
        
        col1, col2, col3 = st.columns(3)
        col1.metric("最新净值", last_price, "", delta_color="inverse")
        
        flow['操作时间'] = pd.to_datetime(flow['操作时间']).dt.strftime('%Y-%m-%d')
        #flow.drop(columns=['操作数'],axis=1,inplace=True) 
        flow.set_index(['产品'],inplace=True)
        st.dataframe(data=flow,width=1500,height=400)
        
        df_price=df_price.set_index( df_price['日期']).drop(['日期'],axis=1) 
        df_price = df_price[starselect_1]
        figsx=px.line(df_price,width=1200)
        st.plotly_chart(figsx)
    elif model_1 =='产品比对':
        st.subheader('产品比对')
        model_2=st.sidebar.radio('资产类型',('公募','私募')) 
        df_name_new= pd.read_excel(r'.\demo.xlsx',sheet_name='名单')
        df_price=merge_price('私募')
        if model_2 == '公募':
            df_name_new = df_name_new[df_name_new['公私募']=='公募']
            df_price=merge_price('公募')
        elif model_2 == '私募':
            df_name_new = df_name_new[df_name_new['公私募']=='私募'] 
            df_price=merge_price('私募')		
        starselect_1=st.multiselect('选择产品',df_name_new['产品']) 
        df_price=df_price.set_index( df_price['日期']).drop(['日期'],axis=1) 
        df_price = df_price[starselect_1]
        figsx=px.line(df_price,width=1200)
        st.plotly_chart(figsx)

if 'is_logged_in' not in st.session_state:
    st.title('更新时间')
    #st.markdown("<p style='font-size: 20px;'>默认上周结算时间为：2023/04/16</p>", unsafe_allow_html=True)
	
    st.markdown("<p style='font-size: 20px;'>默认每年的结算时间为12月25日", unsafe_allow_html=True)
    
    default_date_w = date(2023, 4, 1)
    default_date_m = date(2023, 4, 16)
    default_date_y_1 = date(2022, 12, 25)
    default_date_y_2 = date(2021, 12, 25)
    default_date_y_3 = date(2020, 12, 25)
    
    login_time_w = st.date_input("请输入上周结算时间：", min_value=datetime(1970, 1, 1), max_value=datetime.now(),value=default_date_w)
    login_time_m = st.date_input("请输入上个月结算时间：", min_value=datetime(1970, 1, 1), max_value=datetime.now(),value=default_date_m)
    login_time_y_1 = st.date_input("请输入2022年结算时间：", min_value=datetime(1970, 1, 1), max_value=datetime.now(),value=default_date_y_1)
    login_time_y_2 = st.date_input("请输入2021年结算时间：", min_value=datetime(1970, 1, 1), max_value=datetime.now(),value=default_date_y_2)
    login_time_y_3 = st.date_input("请输入2020年结算时间：", min_value=datetime(1970, 1, 1), max_value=datetime.now(),value=default_date_y_3)
    if st.button("进入报表"):
        
        st.session_state.is_logged_in = True
        st.session_state.login_time_w = login_time_w
        st.session_state.login_time_m = login_time_m
        st.session_state.login_time_y_1 = login_time_y_1
        st.session_state.login_time_y_2 = login_time_y_2
        st.session_state.login_time_y_3 = login_time_y_3

        # 重新渲染页面
        st.experimental_rerun()
else:
    # 显示新的界面
    app(st.session_state.login_time_w,st.session_state.login_time_m,st.session_state.login_time_y_1,st.session_state.login_time_y_2,st.session_state.login_time_y_3)
    #st.write("这是一个新的界面，登录时间：", st.session_state.login_time)

    
