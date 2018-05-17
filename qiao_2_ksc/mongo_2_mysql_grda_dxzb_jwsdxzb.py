#!/usr/bin/env python3
# -*- coding:utf-8 -*- 
# Created by yaochao at 2018/4/20


import pymongo
import pymysql
from qiao_2_ksc import MYSQL_CONF_DEV, MYSQL_CONF_LOCAL, MONGO_CONF


def main():
    connect = pymysql.connect(**MYSQL_CONF_DEV)
    cursor = connect.cursor()

    client = pymongo.MongoClient(**MONGO_CONF)
    db = client.get_database('datasets')
    collection_detail = db.get_collection('xam_person_detail_514')
    result_cursor = collection_detail.find()
    counter = 0
    # sql
    sql0 = 'INSERT INTO sjzq_grda_dxzb (jmbm,lx,sublx,bm,bz,prj) VALUES (%s,%s,%s,%s,%s,%s)'
    sql1 = 'INSERT INTO sjzq_grda_dxzb (jmbm,lx,bm,bz,prj) VALUES (%s,%s,%s,%s,%s)'
    sql2 = 'INSERT INTO sjzq_grda_dxzb (jmbm,lx,bm,prj) VALUES (%s,%s,%s,%s)'
    sql3 = 'INSERT INTO sjzq_grda_jwsdxzb (jmbm,lx,bm,mc,rq,bz,prj) VALUES (%s,%s,%s,%s,%s,%s,%s)'
    sql4 = 'INSERT INTO sjzq_grda_jwsdxzb (jmbm,lx,mc,rq,bz,prj) VALUES (%s,%s,%s,%s,%s,%s)'
    for i in result_cursor:

        # log progress..
        counter += 1
        print(counter, ' - ', i['_id'])

        # 进行字段提取和加工
        person = i['person']
        BM = person['ehrId']
        PRJ = 1

        # 支付方式
        YLFD = person['payMode']
        if YLFD:
            LX = 1
            YLFDs = YLFD.split('/')
            for i in YLFDs:
                if i == '8':
                    otherPayMode = person['otherPayMode']
                else:
                    otherPayMode = None
                cursor.execute(sql1, (BM, LX, i, otherPayMode, PRJ))

        # 药物过敏
        ehrAllergyl = person['ehrAllergyl']
        if ehrAllergyl:
            LX = 2
            for i in ehrAllergyl:
                allergyId = i['allergyId']
                otherAllergy = i['otherAllergy']
                cursor.execute(sql1, (BM, LX, allergyId, otherAllergy, PRJ))

        # 暴露史
        ehrExposure = person['ehrExposure']
        if ehrExposure:
            LX = 3
            for i in ehrExposure:
                exposureId = i['exposureId']
                cursor.execute(sql1, (BM, LX, exposureId, None, PRJ))

        # 家族史
        ehrFamily = person['ehrFamily']
        if ehrFamily:
            LX = 4
            for i in ehrFamily:
                relaId = i['relaId']  # 1.父亲 2.母亲 3.兄弟姐妹 4.子女
                optionId = i['optionId']  # 选项id
                if optionId == '12':  # 疾病选择其他时，记录具体疾病名称
                    dieaseName = i['dieaseName']
                else:
                    dieaseName = None
                cursor.execute(sql0, (BM, LX, relaId, optionId, dieaseName, PRJ))

        # 遗传疾病
        ehrGenetic = person['ehrGenetic']
        if ehrGenetic:
            LX = 5
            for i in ehrGenetic:
                optionId = i['optionId']  # 选项id
                if optionId == '2':  # 选择2时，记录具体疾病名称。
                    dieaseName = i['diseaseName']
                else:
                    dieaseName = None
                cursor.execute(sql1, (BM, LX, optionId, dieaseName, PRJ))

        # 残疾情况
        ehrDeformity = person['ehrDeformity']
        if ehrDeformity:
            LX = 6
            for i in ehrDeformity:
                optionId = i['optionId']
                if optionId == '8':
                    otherDisName = i['otherDisName']
                else:
                    otherDisName = None
                cursor.execute(sql1, (BM, LX, optionId, otherDisName, PRJ))

        # 厨房排风设施
        kitchenExhaust = person['kitchenExhaust']
        if kitchenExhaust:
            kitchenExhaust = kitchenExhaust.split('/')
            LX = 7
            for i in kitchenExhaust:
                cursor.execute(sql2, (BM, LX, i, PRJ))

        # 燃料类型
        fuelType = person['fuelType']
        if fuelType:
            fuelType = fuelType.split('/')
            LX = 8
            for i in fuelType:
                cursor.execute(sql2, (BM, LX, i, PRJ))

        # 饮水
        waterCode = person['waterCode']
        if waterCode:
            waterCode = waterCode.split('/')
            LX = 9
            for i in waterCode:
                cursor.execute(sql2, (BM, LX, i, PRJ))

        # 厕所
        wcType = person['wcType']
        if wcType:
            wcType = wcType.split('/')
            LX = 10
            for i in wcType:
                cursor.execute(sql2, (BM, LX, i, PRJ))

        # 禽畜栏
        livestockBar = person['livestockBar']
        if livestockBar:
            livestockBar = livestockBar.split('/')
            LX = 11
            for i in livestockBar:
                i = int(i) + 1 # 禽畜栏这个选项和其他的选项不一样，他是从0开始的，所以需要+1，保持和规定的同步
                cursor.execute(sql2, (BM, LX, i, PRJ))

        # 既往史疾病
        ehrPastSicks = person['ehrPastSicks']
        if ehrPastSicks:
            LX = 1
            MC_list = ['无', '高血压', '糖尿病', '冠心病', '慢性阻塞性肺病', '恶性肿瘤', '脑卒中', '严重精神障碍', '肺结核', '肝炎', '其他法定传染病', '职业病',
                       '其他']
            for i in ehrPastSicks:
                optionId = i['optionId']
                diagnosesDate = i['diagnosesDate']
                pastName = i['pastName']
                MC = MC_list[int(optionId) - 1]
                if MC == '无':
                    continue
                cursor.execute(sql3, (BM, LX, optionId, MC, diagnosesDate, pastName, PRJ))

        # 既往史手术
        ehrPastOps = person['ehrPastOps']
        if ehrPastOps:
            LX = 2
            for i in ehrPastOps:
                optionId = i['optionId']
                pastName = i['pastName']
                diagnosesDate = i['diagnosesDate']
                BZ = None
                # 选择第一个选项"无"不插入
                # 疾病名称为"无"不插入
                if pastName == '无' or optionId == '1':
                    continue
                # 疾病名和诊断日期必须有一个才插入
                if pastName or diagnosesDate:
                    cursor.execute(sql4, (BM, LX, pastName, diagnosesDate, BZ, PRJ))

        # 既往史外伤
        ehrPastTraumas = person['ehrPastTraumas']
        if ehrPastTraumas:
            LX = 3
            for i in ehrPastTraumas:
                optionId = i['optionId']
                pastName = i['pastName']
                diagnosesDate = i['diagnosesDate']
                BZ = None
                # 选择第一个选项"无"不插入
                # 疾病名称为"无"不插入
                if pastName == '无' or optionId == '1':
                    continue
                # 疾病名和诊断日期必须有一个才插入
                if pastName or diagnosesDate:
                    cursor.execute(sql4, (BM, LX, pastName, diagnosesDate, BZ, PRJ))

        # 既往史输血
        ehrPastBloods = person['ehrPastBloods']
        if ehrPastBloods:
            LX = 4
            for i in ehrPastBloods:
                optionId = i['optionId']
                bloodReason = i['bloodReason']
                diagnosesDate = i['diagnosesDate']
                BZ = None
                # 选择第一个选项"无"不插入
                # 疾病名称为"无"不插入
                if bloodReason == '无' or optionId == '1':
                    continue
                # 疾病名和诊断日期必须有一个才插入
                if bloodReason or diagnosesDate:
                    cursor.execute(sql4, (BM, LX, bloodReason, diagnosesDate, BZ, PRJ))

        # 每1000次commit一次
        if counter % 1000 == 0:
            connect.commit()

    # 最后提交一次，最后不够1000的
    connect.commit()
    connect.close()


if __name__ == '__main__':
    main()
