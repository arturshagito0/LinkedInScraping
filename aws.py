import boto3
import os
import urllib
import json
import sys
import time

def call_scrape(group_num, headers):
    payload = {"is_first_call": True, "group":group_num, "headers":headers}
    lambda_client = boto3.client('lambda')
    lambda_client.invoke(FunctionName='arn:aws:lambda:eu-west-2:340926960333:function:lambda',
                        InvocationType='Event',
                        LogType='Tail',
                        Payload=json.dumps(payload))

def scrape(groups, headers):
    for g in groups:
        call_scrape(g, headers)
        time.sleep(5)

def update_progress(progress, name):
    barLength = 20 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\r{0} | [{1}] {2}%".format(name, "#"*block + "-"*(barLength-block), round(progress*100, 4))
    sys.stdout.write(text)
    sys.stdout.flush()

def view_files_s3(bucket):
    files = []
    s3 = boto3.resource('s3')
    obj = s3.Bucket(bucket)
    for file in obj.objects.all():
        files.append(file.key)
        
    return files

def delete_all_s3(bucket):
    s3 = boto3.resource('s3')
    obj = s3.Bucket(bucket)
    for file in obj.objects.all():
        s3.Object(bucket, file.key).delete()


def read_progress_new(file_name):
    s3 = boto3.resource('s3')
    try:
        obj = s3.Object("scrapes3", file_name)
        body = obj.get()['Body'].read()
    except Exception:
        print("No counter yet!")
        return
    return body

while(True):
    files = view_files_s3("scrapes3")
    for name in files:
        body = read_progress_new(name)
        if(body):
            body = eval(body)
            iterr = body['counter']
            total = body['total']
            if(total == ""):
                print(f"\n{body['g_id']} | {iterr}")
            else:
                progress = round(int(iterr)/(int(total)-1), 4)
                update_progress(progress, str(body['g_id']))
        else:
            pass
    print("\n")
            
    time.sleep(2)


def kill_lambda(counter_name):
    s3 = boto3.resource("s3")
    obj = s3.Object("scrapes3", counter_name)
    body = obj.get()['Body'].read()
    body = eval(body)
    counter_dict = {'counter':body['counter'], "left":body['left'], "total":body['total'], "combinations":body['combinations'], "g_id":body['g_id'], "lambda_alive":0}
    s3.Bucket("scrapes3").put_object(Key=counter_name, Body=json.dumps(counter_dict))


def kill_all():
    s3 = boto3.resource("s3")
    files = view_files_s3("scrapes3")
    for name in files:
        kill_lambda(name)
        time.sleep(2)
        
