# 作業段階をブランチで分けています

- stage1: UDPのみで完結
- stage2: TCPとUDPを併用

**stage2** ブランチが完成版です。

詳細や使用方法は各ブランチのREADMEを参照してください。


# online-chat-messenger
ソケットを使用したオンラインチャットメッセンジャー

## 使用技術
![Static Badge](https://img.shields.io/badge/-Python-F9DC3E.svg?style=flat&logo=python)： 3.10.12  
![Static Badge](https://img.shields.io/badge/-Linux-FCC624?style=flat&logo=linux&logoColor=black)：Ubuntu 22.04  

## 概要
オンラインでチャットを行えるスクリプトアプリです。  
チャットには複数のクライアントが参加できます。  
チャットルーム作成者がホストとして設定され、ホストが退出した場合、チャットルームが削除されます。  
チャットルームに参加しているクライアントには、最後にメッセージを送信してから一定時間で自動的に退出処理が実行されます。  

## 環境構築
### clone
```
$ git clone git@github.com:fate7bardiche/online-chat-messenger.git
$ cd online-chat-messenger
```

### 実行
サーバー側とクライアント側は、別のタブで実行してください。
先にサーバー側から実行します。
```
## サーバー側
$ pwd
> online-chat-messenger/server
$ python3 server.py
```
```
## クライアント側
$ pwd
> online-chat-messenger/client/
$ python3 client.py
```

## 使い方
サーバー側のタブ内を操作することはありません。
クライアント側のタブから、指示に従って入力します。


### チャットルームの作成、参加
チャット機能を使用するためには、以下の準備が必要です。
- チャットルーム名の指定
- 作成 or 参加の選択
- ユーザー名の入力  

画面の案内の通り入力します。

https://github.com/user-attachments/assets/5767057b-2baa-43b7-bc03-a2d378938166

### チャットルーム
チャット内の画面です。  
文字を入力しエンターでメッセージを送信します。  
もし他にチャットルームに参加者がいた場合、他参加者が送信したメッセージも表示されます。  

https://github.com/user-attachments/assets/5ab4e125-4681-491e-876b-0dcbf15c24a8

### 退出
3つの退出方法があります。  
退出したあと他のチャットルームを作成・参加する場合には、クライアントプログラムを再実行して下さい

1. Ctrl+C またはプロセスを kill して退出

    退出した際は、他の参加者に退出を知らせるメッセージが送信されます。

2. ホストが退出

    ホストが退出した場合は、他の参加者全員に退出処理が実行されます。その後チャットルームが削除されます。

3. 一定時間が経過

   最後にメッセージを送信してから一定時間が経過すると、自動的に退出されます。自動退出までの秒数はチャット参加時に表示されます。

https://github.com/user-attachments/assets/5767057b-2baa-43b7-bc03-a2d378938166
  

![スクリーンショット 2025-04-22 15 39 23](https://github.com/user-attachments/assets/00c4126b-2735-4dd7-a73c-aa8191bc451b)


## TODO: 実装したかったこと
チャットから退出したユーザーの処理をUDPからTCPの処理に戻す。プログラムを起動した時と同じように、チャット作成の導線が再表示されるようにしたい。