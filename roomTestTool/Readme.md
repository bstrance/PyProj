# Chirpy

■フォルダ構成  
┃roomTestTool┃  
┣result(出力結果先)  
┣chirpy.exe(実行ファイル)  
┣checkDevice.exe(Device index確認用)  
　※TASCAM US-2X2を使用する場合は基本的にIndexは1だがインターフェイスやPCによってはズレるため予め確認しておくこと
1. フォルダを以下の場所に設置
*Dolby_Atmos_XXXXXXXX_Products_XXXXX/Test_Tools*  
2. chirpy.exeを実行

●Option  
-h,　-help
*************************************************************
Auto Chirp test tool.
chirpy.exe args[1] args[2] args[3] args[4] or help options
Arguments below:
args[1] : rec wait time.(Default 10)
args[2] : csv window time.(Default 6)
args[3] : Output file name.
args[4] : Speaker Position. Select ltm/rtm.
args[5] : (Option)Interface device index.
*************************************************************

例: lreというファイル名でltm側の測定を行う。  
*C:\Dolby\Dolby_Atmos_XXXXXXXXX\Test_Tools\roomTestTool>chirpy.exe 10 6 lre ltm*  

C:\Users\hityamada\Desktop\Dolby_Atmos_For_Home_Theater\Test_Tools\roomTestTool>chirpy.exe 10 6 lre ltm  
[SEC: Send Stream]  
** Not used NVIDIA CARDS! The following error is okay. **  
Failed to init NVIDIA API (This is expected when no NVIDIA video cards are present)←DolbyTool側のAlert**なので無視    
[SEC: Start recording]  
End recording......  
saved: 2018_06_06_13_31_11_lre_rtm.wav !  
[SEC: Create CSV file]  
Saved: 2018_06_06_13_31_11_lre_rtm.wav.csv !  
[Done!]  