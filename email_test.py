import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from time import time

import asyncio
import tornado
import tornado.web

import aiosmtplib


async def sendemail(my_user, code, my_sender = '546397335@qq.com', my_pass = 'azbftecmmszbbcea'):
    start = time()
    ret = True
    msg = MIMEText("验证码:" + code, 'plain', 'utf-8')
    msg['From'] = formataddr(["zzx", my_sender])
    msg['To'] = formataddr(["尊敬的用户", my_user])
    msg['Subject'] = "注册邮箱验证"
    try:
        async with aiosmtplib.SMTP(hostname="smtp.qq.com", port=465,use_tls=True) as smtp:
            await smtp.login(my_sender, my_pass)
            await smtp.send_message(msg)
    except aiosmtplib.SMTPException as e:
        pass
        #
        # server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
        # server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        # server.sendmail(my_sender, [my_user, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        # server.quit()  # 关闭连接

    end = start-time()
    print(end)
    # except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
    #     ret = False
    # return ret

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sendemail('546397335@qq.com','2122'))

