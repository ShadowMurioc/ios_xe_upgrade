import threading
from netmiko import ConnectHandler
import time
from Data import ipData
from queue import Queue


ipna = ipData.ipinfo
user = 'admin'
pwd = 'C1sc0123'
IMAGE_File = 'c1100-universalk9.17.06.02.SPA.bin'
FTP_SRV = '172.16.41.119'
FTP_USER = 'transfer'
FTP_PASS = "A0f3rNPgpK91"
thread_nums = 5
limit_thread = threading.BoundedSemaphore(value=thread_nums)


def ssh_netmiko(ip, user, pwd, queue):
    try:
        limit_thread.acquire()
        device_ssh = {
                        'device_type': 'cisco_ios',
                        'ip': ip,
                        'username': user,
                        'password': pwd,
                        'read_timeout_override': 2400
                    }
        time.sleep(0.5)
        print("正在连接" + device_ssh['ip'] )
        ssh_netconnect = ConnectHandler(**device_ssh)
        print("交换机" + device_ssh['ip'] + ' 成功连接')
        time1 = time.strftime("%Y-%m-%d_%H:%M:%S")
        start = time.time()
        print(ip + '  版本升级开始时间  ' + time1)
        print('正在下载镜像 =====> {}'.format(IMAGE_File))
        Transfer_Image = ssh_netconnect.send_command('copy ftp://{}:{}@{}/{} bootflash:'.format(FTP_USER, FTP_PASS, FTP_SRV, IMAGE_File), expect_string=r'.bin]?')
        Transfer_Image += ssh_netconnect.send_command('{}'.format(IMAGE_File), expect_string=r'#')
        print(device_ssh['ip'] + '  镜像已经下载完成，开始安装新版本文件=== {} ==='.format(IMAGE_File))
        Install_Image = ssh_netconnect.send_command('request platform software sdwan software install bootflash:{}'.format(IMAGE_File), expect_string=r'#')
        # 以下可以查看当前sdwan software的状态
        # show = ssh_netconnect.send_command('show sdwan software', expect_string=r'#')
        # print(show)
        print(device_ssh['ip'] + '新版本文件=== {} ===设置默认启动'.format(IMAGE_File))
        image_set_default = ssh_netconnect.send_command('request platform software sdwan software set-default 17.06.02.0.2786',  expect_string=r'#')
        # 以下可以查看当前sdwan software 与前面状态做相应对比。
        # show_new = ssh_netconnect.send_command('show sdwan software', expect_string=r'#')
        # print(show_new)
        print(device_ssh['ip'] + '新版本文件=== {} ===确认进行升级'.format(IMAGE_File))
        upgrade_confirm = ssh_netconnect.send_command('request platform software sdwan software upgrade-confirm', expect_string=r'#')
        # 激活软件后会自动重启
        print(device_ssh['ip'] + '新版本文件=== {} ===重置'.format(IMAGE_File))
        # activate_confirm = ssh_netconnect.send_command('request platform software sdwan software reset', expect_string=r'#')
        activate_confirm = ssh_netconnect.send_command('request platform software sdwan software reset')
        # print('新版本文件=== {} ===激活确认'.format(IMAGE_File))
        # activate_confirm = ssh_netconnect.send_command('request platform software sdwan software activate 17.06.02.0.2786', expect_string=r'#')
        time2 = time.strftime("%Y-%m-%d_%H:%M:%S")
        end = time.time()
        print(ip + '  版本升级结束时间  ' + time2)
        print(ip + '   版本升级时间持续 %.6f'%(end - start) + ' 秒')
        ssh_netconnect.disconnect()
        limit_thread.release()
    except Exception as e:
        time.sleep(0.5)
        print('Failed to Device', ip)
        time.sleep(0.5)
        limit_thread.release()
    # except netmiko_exceptions as e:
    #     print('Failed to Device', ip, e)


if __name__ == '__main__':
    threads = []
    while 1 == 1:
        for ip in ipna:
            t1 = threading.Thread(target=ssh_netmiko, args=(ip, user, pwd, Queue()))
            t1.start()
            threads.append(t1)
        for th in threads:
            th.join()
