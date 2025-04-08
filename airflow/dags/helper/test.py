from datetime import datetime, timedelta
def testf():
    sum = 0
    for i in range(5):
        sum += i
    return sum

def task_date(ti):
    # 以2021/05/30為例 格式為 date="20210530"
    execute_date = datetime.today() - timedelta(days=1)
    execute_date = execute_date.strftime('%Y%m%d')

    # XCom push file name in gcs and date
    return {'date':execute_date}