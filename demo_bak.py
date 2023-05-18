import pandas as pd
import streamlit as st
import plotly_express as px
import time
import requests
import json
import re
from collections import deque



st.set_page_config(layout='wide')

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
	print("#############	当年	   ################")
	print("################################################")
	amount_list = []
	hold_list = []
	hold_profit_list = []
	sold_profit_list = []
	total_profit_list = []
	cost_list = []
	last_price_list = []
	buy_list = []
	sell_list = []
	alive_list = []
	current_buy_list = []
	current_sell_list = []
	current_buy_amount_list = []
	current_sell_amount_list = []
	start_year_time =pd.Timestamp("2023-12-31 00:00:00")
	#start_month_time =pd.Timestamp("2023-03-31 00:00:00")
	#start_week_time =pd.Timestamp("2023-04-16 00:00:00")
	
	for row in name:
		cost = 0
		amount = 0
		hold_profit = 0
		sold_profit = 0
		buy = 0
		sell = 0
		current_buy = 0
		current_sell = 0
		current_buy_amount = 0
		current_sell_amount = 0
		flow = df_flow[(df_flow['产品'].isin([row]))]
		print("------------"+row+"------------")
		flow_list = flow.values.tolist()
		for one_flow in flow_list:
			print(one_flow[1], one_flow[2], one_flow[3])
			price = df_price[(df_price['日期'].isin([one_flow[1]]))][row].values.tolist()[0]
			print(price)
			if one_flow[2] == '申购买入':
				cost = (cost * amount + one_flow[3]) / (amount + one_flow[4])   
				amount = amount + one_flow[4]
				buy = buy + one_flow[3]
				if one_flow[1] > start_year_time:
					current_buy = 1
					current_buy_amount = current_buy_amount + one_flow[3]
			elif one_flow[2] == '认购买入':
				price = 1
				cost = (cost * amount + one_flow[3]) / (amount + one_flow[4])
				amount = amount + one_flow[4]
				buy = buy + one_flow[3]
				if one_flow[1] > start_year_time:
					current_buy = 1
					current_buy_amount = current_buy_amount + one_flow[3]
			elif one_flow[2] == '赎回卖出':
				sold_profit = sold_profit + one_flow[3] - cost * one_flow[4]
				sell = sell + one_flow[3]
				if (amount - one_flow[4]) < 5 and (amount - one_flow[4]) > -5:
					amount = 0
				else:
					amount = amount - one_flow[4]
				if one_flow[1] > start_year_time:
					current_sell = 1
					current_sell_amount = current_sell_amount + one_flow[3]
			elif one_flow[2] == '现金分红':
				sold_profit = sold_profit + one_flow[3]
				sell = sell + one_flow[3]
			elif one_flow[2] == '份额分红':
				cost = cost * amount  / (amount + one_flow[4])
				amount = amount + one_flow[4]
				#sold_profit = sold_profit + one_flow[4] * (price - cost)  
		last_price = 0
		for one_price in df_price[row].values.tolist():
			if one_price:
				last_price = one_price
		print('last', last_price)
		hold_profit = (last_price - cost) * amount
		amount_list.append(round(amount))
		hold_list.append(round(amount * last_price))
		hold_profit_list.append(round(hold_profit))
		sold_profit_list.append(round(sold_profit))
		total_profit_list.append(round(hold_profit+ sold_profit))
		cost_list.append(cost)
		last_price_list.append(last_price)
		buy_list.append(buy)
		sell_list.append(sell)
		if round(amount) == 0:
			alive_list.append(0)
		else:
			alive_list.append(1)
		current_buy_list.append(current_buy)
		current_sell_list.append(current_sell)
		current_buy_amount_list.append(current_buy_amount)
		current_sell_amount_list.append(current_sell_amount)
			
	df_name = df_name[(df_name['产品'].isin(name))]
	df_name['成本价']=cost_list 
	df_name['当前净值']=last_price_list
	df_name['持有数量']=amount_list
	df_name['目前产品数量']=alive_list
	
	df_name['投资总金额']=buy_list 
	df_name['卖出总金额']=sell_list
	df_name['持有金额']=hold_list 
	df_name['本年新投']=current_buy_list
	df_name['本年赎回']=current_sell_list
	df_name['本年新投本金']=current_buy_amount_list
	df_name['本年赎回金额']=current_sell_amount_list
	 
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
		end_time_0 =pd.Timestamp("2023-04-16 00:00:00")
		last_time_0 =pd.Timestamp("2023-04-16 00:00:00")
		end_time_1 =pd.Timestamp("2023-04-01 00:00:00")
		last_time_1 =pd.Timestamp("2023-04-01 00:00:00")
		end_time_2 =pd.Timestamp("2022-12-25 00:00:00")
		last_time_2 =pd.Timestamp("2022-12-25 00:00:00")
		end_time_3 =pd.Timestamp("2021-12-25 00:00:00")
		last_time_3 =pd.Timestamp("2021-12-25 00:00:00")
		end_time_4 =pd.Timestamp("2020-12-25 00:00:00")
		last_time_4 =pd.Timestamp("2020-12-25 00:00:00")
		
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

	print("################################################")
	print("#############		上周	  ################")
	print("################################################")
	amount_list = []
	hold_list = []
	hold_profit_list = []
	sold_profit_list = []
	total_profit_list_last = []
	total_profit_list_current = []
	total_profit_list_current_pos = []
	total_profit_list_current_pos_amount = []
	total_profit_list_current_neg = []
	total_profit_list_current_neg_amount = []
	cost_list = []
	last_price_list = []
	alive_list = []
	for row in name:
		cost = 0
		amount = 0
		hold_profit = 0
		sold_profit = 0
		flow = df_flow[(df_flow['产品'].isin([row]))]
		print("------------"+row+"------------")
		flow_list = flow.values.tolist()
		last_time = last_time_list[row][0]
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
		hold_list.append(round(amount * last_price))
		hold_profit_list.append(round(hold_profit))
		sold_profit_list.append(round(sold_profit))
		total_profit_list_last.append(round(hold_profit+ sold_profit))
		index = len(total_profit_list_last) - 1
		total_profit_list_current.append(total_profit_list[index] - round(hold_profit+ sold_profit))
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
		if round(amount) == 0:
			alive_list.append(0)
		else:
			alive_list.append(1)

	df_name['本周浮盈数量']=total_profit_list_current_pos
	df_name['本周浮盈金额']=total_profit_list_current_pos_amount
	df_name['本周浮亏数量']=total_profit_list_current_neg
	df_name['本周浮亏金额']=total_profit_list_current_neg_amount 

	print("################################################")
	print("#############		上月	  ################")
	print("################################################")
	amount_list = []
	hold_list = []
	hold_profit_list = []
	sold_profit_list = []
	total_profit_list_last = []
	total_profit_list_current = []
	total_profit_list_current_pos = []
	total_profit_list_current_pos_amount = []
	total_profit_list_current_neg = []
	total_profit_list_current_neg_amount = []
	cost_list = []
	last_price_list = []
	alive_list = []
	for row in name:
		cost = 0
		amount = 0
		hold_profit = 0
		sold_profit = 0
		flow = df_flow[(df_flow['产品'].isin([row]))]
		print("------------"+row+"------------")
		flow_list = flow.values.tolist()
		last_time = last_time_list[row][1]
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
		hold_list.append(round(amount * last_price))
		hold_profit_list.append(round(hold_profit))
		sold_profit_list.append(round(sold_profit))
		total_profit_list_last.append(round(hold_profit+ sold_profit))
		index = len(total_profit_list_last) - 1
		total_profit_list_current.append(total_profit_list[index] - round(hold_profit+ sold_profit))
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
		if round(amount) == 0:
			alive_list.append(0)
		else:
			alive_list.append(1)

	df_name['本月浮盈浮亏']=total_profit_list_current
	df_name['本月浮盈产品数量']=total_profit_list_current_pos
	df_name['本月浮盈金额']=total_profit_list_current_pos_amount
	df_name['本月浮亏产品数量']=total_profit_list_current_neg
	df_name['本月浮亏金额']=total_profit_list_current_neg_amount 
	df_name['上月盈利']=total_profit_list_last

	print("################################################")
	print("#############		2022年	  ################")
	print("################################################")
	amount_list = []
	hold_list = []
	hold_profit_list = []
	sold_profit_list = []
	total_profit_list_last = []
	total_profit_list_current = []
	total_profit_list_current_pos = []
	total_profit_list_current_pos_amount = []
	total_profit_list_current_neg = []
	total_profit_list_current_neg_amount = []
	cost_list = []
	last_price_list = []
	alive_list = []
	for row in name:
		cost = 0
		amount = 0
		hold_profit = 0
		sold_profit = 0
		flow = df_flow[(df_flow['产品'].isin([row]))]
		print("------------"+row+"------------")
		flow_list = flow.values.tolist()
		last_time = last_time_list[row][2]
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
		hold_list.append(round(amount * last_price))
		hold_profit_list.append(round(hold_profit))
		sold_profit_list.append(round(sold_profit))
		total_profit_list_last.append(round(hold_profit+ sold_profit))
		index = len(total_profit_list_last) - 1
		total_profit_list_current.append(total_profit_list[index] - round(hold_profit+ sold_profit))
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
		if round(amount) == 0:
			alive_list.append(0)
		else:
			alive_list.append(1)

	df_name['本年累计浮盈']=total_profit_list_current
	df_name['本年浮盈产品数量']=total_profit_list_current_pos
	df_name['本年浮盈金额']=total_profit_list_current_pos_amount
	df_name['本年浮亏产品数量']=total_profit_list_current_neg
	df_name['本年浮亏金额']=total_profit_list_current_neg_amount
	df_name['上年结转']=alive_list
	df_name['年初结转金额']=hold_list
		
	df_name['2022年持有收益']=hold_profit_list
	df_name['2022年了结收益']=sold_profit_list
	df_name['2022年汇总收益']=total_profit_list_last


	print("################################################")
	print("#############		2021年	  ################")
	print("################################################")
	amount_list = []
	hold_list = []
	hold_profit_list = []
	sold_profit_list = []
	total_profit_list = []
	cost_list = []
	last_price_list = []
	for row in name:
		cost = 0
		amount = 0
		hold_profit = 0
		sold_profit = 0
		flow = df_flow[(df_flow['产品'].isin([row]))]
		print("------------"+row+"------------")
		flow_list = flow.values.tolist()
		last_time = last_time_list[row][3]
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
		hold_list.append(round(amount * last_price))
		hold_profit_list.append(round(hold_profit))
		sold_profit_list.append(round(sold_profit))
		total_profit_list.append(round(hold_profit+ sold_profit))
		cost_list.append(cost)
		last_price_list.append(last_price)

	
	df_name['2021年持有收益']=hold_profit_list
	df_name['2021年了结收益']=sold_profit_list
	df_name['2021年汇总收益']=total_profit_list


	print("################################################")
	print("#############		2020年	  ################")
	print("################################################")
	amount_list = []
	hold_list = []
	hold_profit_list = []
	sold_profit_list = []
	total_profit_list = []
	cost_list = []
	last_price_list = []
	for row in name:
		cost = 0
		amount = 0
		hold_profit = 0
		sold_profit = 0
		flow = df_flow[(df_flow['产品'].isin([row]))]
		print("------------"+row+"------------")
		flow_list = flow.values.tolist()
		last_time = last_time_list[row][4]
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
		hold_list.append(round(amount * last_price))
		hold_profit_list.append(round(hold_profit))
		sold_profit_list.append(round(sold_profit))
		total_profit_list.append(round(hold_profit+ sold_profit))
		cost_list.append(cost)
		last_price_list.append(last_price)

	df_name['2020年持有收益']=hold_profit_list
	df_name['2020年了结收益']=sold_profit_list
	df_name['2020年汇总收益']=total_profit_list

	return df_name
	
def summary(type):
	df_1= pd.read_excel(r'.\总表.xlsx',sheet_name=type)
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
	df_name = st.session_state.df_name
	model_2=st.sidebar.radio('统计维度',('整体','年度','月度','周度')) 
	st.subheader('总体情况——'+model_2)
	df_all = summary(model_2)
	df_1 = df_name.groupby(['投资产品类型'])['投资总金额'].sum()
	df_2 = df_name.groupby(['投资产品类型'])['目前产品数量'].sum()
	df_3 = df_name.groupby(['投资产品类型'])['本年新投'].sum()
	df_4 = df_name.groupby(['投资产品类型'])['本年赎回'].sum()
	df_5 = df_name.groupby(['投资产品类型'])['本年新投本金'].sum()
	df_6 = df_name.groupby(['投资产品类型'])['本年赎回金额'].sum()
	df_7 = df_name.groupby(['投资产品类型'])['上年结转'].sum()
	df_8 = df_name.groupby(['投资产品类型'])['年初结转金额'].sum()
	df_9 = df_name.groupby(['投资产品类型'])['本年累计浮盈'].sum()
	df_10 = df_name.groupby(['投资产品类型'])['本年浮盈产品数量'].sum()
	df_11 = df_name.groupby(['投资产品类型'])['本年浮盈金额'].sum()
	df_12 = df_name.groupby(['投资产品类型'])['本年浮亏产品数量'].sum()
	df_13 = df_name.groupby(['投资产品类型'])['本年浮亏金额'].sum()
	df_14 = df_name.groupby(['投资产品类型'])['本月浮盈浮亏'].sum()
	df_15 = df_name.groupby(['投资产品类型'])['本月浮盈产品数量'].sum()
	df_16 = df_name.groupby(['投资产品类型'])['本月浮盈金额'].sum()
	df_17 = df_name.groupby(['投资产品类型'])['本月浮亏产品数量'].sum()
	df_18 = df_name.groupby(['投资产品类型'])['本月浮亏金额'].sum()
	df_19 = df_name.groupby(['投资产品类型'])['上月盈利'].sum()
	df_20 = df_name.groupby(['投资产品类型'])['本周浮盈数量'].sum()
	df_21 = df_name.groupby(['投资产品类型'])['本周浮盈金额'].sum()
	df_22 = df_name.groupby(['投资产品类型'])['本周浮亏数量'].sum()
	df_23 = df_name.groupby(['投资产品类型'])['本周浮亏金额'].sum()
	if model_2 == '整体':
		df_all['投资总金额'] = df_1
		df_all['目前产品数量'] = df_2
		df_all['本年新投'] = df_3
		df_all['本年赎回'] = df_4
		df_all['本年新投本金'] = df_5
		df_all['本年赎回金额'] = df_6
		df_all['上年结转'] = df_7
		df_all['年初结转金额'] = df_8
		st.dataframe(data=df_all,width=1500,height=400)
	elif model_2 == '年度':
		df_all['本年累计浮盈'] = df_9
		df_all['本年浮盈产品数量'] = df_10
		df_all['本年浮盈金额'] = df_11
		df_all['本年浮亏产品数量'] = df_12
		df_all['本年浮亏金额'] = df_13
		st.dataframe(data=df_all,width=1500,height=400)
	elif model_2 == '月度':
		df_all['本月浮盈浮亏'] = df_14
		df_all['本月浮盈产品数量'] = df_15
		df_all['本月浮盈金额'] = df_16
		df_all['本月浮亏产品数量'] = df_17
		df_all['本月浮亏金额'] = df_18
		df_all['上月盈利'] = df_19
		st.dataframe(data=df_all,width=1500,height=400)
	elif model_2 == '周度':
		df_all['本周浮盈数量'] = df_20
		df_all['本周浮盈金额'] = df_21
		df_all['本周浮亏数量'] = df_22
		df_all['本周浮亏金额'] = df_23
		st.dataframe(data=df_all,width=1500,height=400)
	df_excel_1 = pd.DataFrame()
	df_excel_1['目前产品数量'] = df_2
	df_excel_1['本年新投'] = df_3
	df_excel_1['本年赎回'] = df_4
	df_excel_1['上年结转'] = df_7
	df_excel_1.columns = pd.MultiIndex.from_product([['产品情况'],['目前产品数量', '本年新投','本年赎回','上年结转']])
	
	df_excel_2 = pd.DataFrame()
	df_excel_2['投资总金额'] = df_1
	df_excel_2['本年新投本金'] = df_5
	df_excel_2['本年赎回金额'] = df_6
	df_excel_2['年初结转金额'] = df_8
	df_excel_2.columns = pd.MultiIndex.from_product([['资金情况'],['投资总金额', '本年新投本金','本年赎回金额','年初结转金额']])
	
	df_excel_3 = pd.DataFrame()
	df_excel_3['本年累计浮盈'] = df_9
	df_excel_3['本年浮盈产品数量'] = df_10
	df_excel_3['本年浮盈金额'] = df_11
	df_excel_3['本年浮亏产品数量'] = df_12
	df_excel_3['本年浮亏金额'] = df_13
	df_excel_3.columns = pd.MultiIndex.from_product([['本年情况'],['本年累计浮盈', '本年浮盈产品数量','本年浮盈金额','本年浮亏产品数量', '本年浮亏金额']])
	
	df_excel_4 = pd.DataFrame()
	df_excel_4['本月浮盈浮亏'] = df_14
	df_excel_4['本月浮盈产品数量'] = df_15
	df_excel_4['本月浮盈金额'] = df_16
	df_excel_4['本月浮亏产品数量'] = df_17
	df_excel_4['本月浮亏金额'] = df_18
	df_excel_4['上月盈利'] = df_19
	df_excel_4.columns = pd.MultiIndex.from_product([['本月情况'],['本月浮盈浮亏', '本月浮盈产品数量','本月浮盈金额','本月浮亏产品数量','本月浮亏金额','上月盈利']])
	
	df_excel_5 = pd.DataFrame()
	df_excel_5['本周浮盈数量'] = df_20
	df_excel_5['本周浮盈金额'] = df_21
	df_excel_5['本周浮亏数量'] = df_22
	df_excel_5['本周浮亏金额'] = df_23
	df_excel_5.columns = pd.MultiIndex.from_product([['本周情况'],['本周浮盈数量', '本周浮盈金额','本周浮亏数量','本周浮亏金额']])
	
	df_all = pd.concat([df_excel_1, df_excel_2, df_excel_3, df_excel_4, df_excel_5], axis=1, sort=True)
	
	df_2= pd.read_excel(r'.\demo.xlsx',sheet_name='名单')
	type_list = df_2['投资产品类型'].unique()
	class_1 = []
	class_2 = []
	for one_type in type_list:
		class_2.append(one_type)
		class_1.append(df_2[(df_2['投资产品类型'].isin([one_type]))]['公私募'].values.tolist()[0])
	df_all.index = pd.MultiIndex.from_arrays([class_1,class_2])
	df_all.to_excel('all.xlsx', index=True)
	with open('all.xlsx', 'rb') as my_file:
		st.sidebar.download_button(label = '下载', data = my_file, file_name = '汇总.xlsx', mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')  
elif model_1 == '产品类型':
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
	df_name_new = df_name_new.drop(columns=['公私募','投资产品类型', '目前产品数量','本年新投','本年赎回','本周浮盈数量','本周浮亏数量','本月浮盈产品数量','本月浮亏产品数量','本年浮盈产品数量','本年浮亏产品数量','上年结转','本月浮盈浮亏','本年累计浮盈'],axis=1)
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

#st.dataframe(data=df_value,width=None,height=None)
#st.dataframe(data=buy_in,width=None,height=None)
#st.dataframe(data=buy_out,width=None,height=None)








