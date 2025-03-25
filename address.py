
#「ADD：入力内容の登録」
def AddFunc():
    global Userdict
    name = input("名前を入力してください：")
    phoneNum = input("メールアドレスを入力してください：")    
    age = input("メモを入力してください：")
    info = (name,phoneNum, age)

    if len(Userdict.keys()) == 10:
        print("\n追加できる件数は10件までです！\nメニュー画面に戻ります。\n---------")
        return
    
    elif Userdict == {}:
        #ユーザの情報が入力されていないのであればID１を入れて登録
        Userdict[1] = info
        print("\n~入力された情報を登録しました~\n---------")
        while True:
            moreCheck = input("追加で登録しますか？(y|n)：")
            print("")
            if moreCheck == "y" or moreCheck == "ｙ":
                AddFunc()
                break
            
            elif moreCheck == "n" or moreCheck == "ｎ":
                print("メニュー画面に戻ります。\n---------")
                return
                
            else:
                print("その入力は無効です。再入力してください。\n---------")
                continue
        
    else:
        ids = list(Userdict.keys())
        last_id = ids[-1]
        Userdict[last_id + 1] = info
        print("\n~入力された情報を登録しました~\n---------")
        while True:
            moreCheck = input("追加で登録しますか？(y|n)：")
            print("")
            if moreCheck == "y" or moreCheck == "ｙ":
                AddFunc()
                break
            
            elif moreCheck == "n" or moreCheck == "ｎ":
                print("メニュー画面に戻ります。\n---------")
                return           
            
            else:
                print("その入力は無効です。")
                continue
                

#「VIEW：登録内容の表示」
def ViewFunc():
    if Userdict == {}:
        print("登録件数が0件です！\n\nメニュー画面に戻ります。\n---------")
        return
    
    else:
        ids = list(Userdict.keys())
        print(f"~現在{len(ids)}件の登録があります~\n")
        # # 昇順で並び変えてから表示
        # sorted_ids = sorted(ids)
        for id in ids:
            print("ID",id,":",Userdict[id])
        
        print("\nメニュー画面に戻ります。\n---------")
        return


#「DELETE：登録内容の削除」    
def DeleteFunc():
    global Userdict 
    if Userdict == {}:
        print("登録件数が0件です！\n\nメニュー画面に戻ります。\n---------")
        return
    
    else:
        try:
            deleteId = int(input("削除対象とするIDを入力してください。\nID："))
            if deleteId in set(Userdict.keys()):
                del Userdict[deleteId]
                print("\n~入力された登録情報を削除しました~\n---------")
                
                while Userdict != {}:
                    moreCheck = input("追加で削除しますか？(y|n)：")
                    print("")
                    if moreCheck == "y" or moreCheck == "ｙ":
                        DeleteFunc()
                        break
                    
                    elif moreCheck == "n" or moreCheck == "ｎ":
                        print("メニュー画面に戻ります。\n---------")
                        return           
                    
                    else:
                        print("その入力は無効です。")
                        continue
                
            else:
                print("\n入力されたIDは存在しません！\n---------")
                DeleteFunc()
        
        except ValueError:
                print("\n入力されたIDは存在しません！\n---------")
                DeleteFunc()
        
if __name__ == "__main__":
    
    #ユーザの入力情報を保持しておく辞書
    Userdict = {}
    
    while True:
        print("#######\n1.ADD\n2.VIEW\n3.DELETE\n4.END\n#######\n")
        userChoice = input("1～4の番号を入力してください：")
        print("---------")
        if userChoice in ("1","2","3","4") or userChoice in ("１","２","３","４"):
            if userChoice == "1" or userChoice == "１":
                AddFunc()
                
            elif userChoice == "2" or userChoice == "２":
                ViewFunc()
                
            elif userChoice == "3" or userChoice == "３":
                DeleteFunc()
                
            else:#ENDが選ばれたら終了
                print("終了します。\n---------")
                break
                
        else:
            print("その入力は無効です。再入力してください。\n---------")
            continue
        

        
    