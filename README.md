# 作業段階をブランチで分けています
stage2ブランチが最新です。  
- stage1: UDPのみで完結  
- stage2: TCPとTCPで実装

 使用方法は各ブランチのREADMEを参照してください。


# online-chat-messenger
ソケットを使用した、オンラインチャットメッセンジャー

## 使用技術
![Static Badge](https://img.shields.io/badge/-Python-F9DC3E.svg?style=flat&logo=python)： 3.10.12  
![Static Badge](https://img.shields.io/badge/-Linux-FCC624?style=flat&logo=linux&logoColor=black)：Ubuntu 22.04  

## 使い方
クライアントとサーバーでタブを分けて起動します。
```
$ ~/online-chat-messenger/server
$ python3 server.py 
```
```
$ ~/online-chat-messenger/client
$ python3 client.py 
```
https://github.com/user-attachments/assets/d42c3708-de4a-499b-ac04-2c0e93d5e3ae

