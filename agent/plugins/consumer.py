# -*- encoding: utf-8 -*-
import requests
import logging

def consumer(queue, server_ip, server_port):
    while True:
        logger = logging.getLogger()
        q = queue
        logger.info("receive queue")
        content = q.get()
        type = content['type']
        msg = content['msg']
        client_ip = content['ip']
        if type == 'client':
            url = f'http://{server_ip}:{server_port}/api/v1/client/{client_ip}/'
            req = requests.post(url, json=msg)
            if req.status_code == 200:
                logger.info(f"send host info success. {req.text}")
            else:
                logger.warning(f"send host info failure. {req.text}")
        elif type == 'resource':
            url = f'http://{server_ip}:{server_port}/api/v1/client/{client_ip}/resource/'
            req = requests.post(url, json=msg)
            if req.status_code == 200:
                logger.info(f"send resource info success. {req.text}")
            else:
                logger.warning(f"send resource info failure. {req.text}")
        elif type == 'heartbeat':
            url = f'http://{server_ip}:{server_port}/api/v1/client/{client_ip}/heartbeat/'
            req = requests.post(url)
            if req.status_code == 200:
                logger.info(f"send heartbeat info success. {req.text}")
            else:
                logger.warning(f"send heartbeat info failure. {req.text}")