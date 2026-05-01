# 软件拦截卫士 (Python版) v2.0

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> 一款用Python编写的系统保护工具，专门用于拦截鲁大师、360、2345等流氓软件的自动安装和广告推送。

## 功能特性

### v2.0 核心功能

- **强制管理员提权** - 程序启动自动获取管理员权限，双击直接运行
- **安装进程秒杀** - 检测到安装程序立即杀死，阻止安装
- **白名单保护** - 不误杀360急救箱、Steam、GitHub、火绒、UU加速器等正常软件
- **进程监控拦截** - 实时监控并终止可疑安装程序
- **Hosts文件拦截** - 自动修改Hosts文件阻断广告域名
- **注册表保护** - 阻止流氓软件添加开机启动项
- **文件监控** - 自动识别并删除可疑安装包
- **系统托盘** - 最小化到托盘，后台持续保护

### 附加功能
- **Hosts自动备份** - 每次修改前自动备份原hosts
- **一键还原** - 可恢复到任意历史备份版本
- **域名白名单** - 避免误拦截正常网站
- **智能规则校验** - 避免重复写入hosts，防止hosts文件被写爆

## 环境要求

- **Windows 7/10/11**
- **Python 3.8 或更高版本**
- 已自动获取管理员权限，无需手动操作

### 安装Python

如果还没有安装Python：
1. 访问 https://www.python.org/downloads/
2. 下载 Python 3.8+ 版本
3. 安装时勾选 **"Add Python to PATH"**

## 快速开始

### 方法一：直接双击运行（推荐）

1. 下载本项目所有文件
2. 解压到任意文件夹（如 `D:\SoftwareBlocker`）
3. **双击运行 `main.py`**
4. 程序自动获取管理员权限并启动

### 方法二：使用批处理启动

```bash
双击运行 run_as_admin.bat
```

### 方法三：静默启动（无窗口）

双击运行 `silent_start.vbs`，程序在后台静默运行

## 文件说明

```
SoftwareBlocker/
├── main.py                 # 主程序源码（自动管理员提权）
├── requirements.txt        # Python依赖包列表
├── run_as_admin.bat       # 管理员权限启动脚本
├── silent_start.vbs       # 静默启动脚本
├── config/
│   └── config.json        # 拦截规则配置文件（自动生成）
│   └── block_log.txt      # 拦截日志（自动生成）
├── backup/                # Hosts备份目录（自动生成）
└── README.md              # 本文件
```

## 安装进程秒杀功能

程序会自动检测并杀死以下关键词的安装程序：

```
360setup, 2345setup, LDSsetup, ludashi, 鲁大师, 
haozip, duba, jinshan, pcmgr, qqpcmgr
```

一旦检测到包含这些关键词的进程，**立即强制杀死**，阻止安装！

## 白名单保护

以下软件受到保护，**不会被拦截、不会被删除**：

### 360急救箱系列
- 360急救箱.exe
- 360SysRepair.exe
- 360EmergencyBox.exe
- 360Rs.exe
- 360Repair.exe
- 360SysAssist.exe

### 正常软件
- Steam (steam.exe, steamwebhelper.exe)
- GitHub (github.exe, git.exe)
- 火绒安全 (huorong.exe, hips.exe, hrkill.exe)
- UU加速器 (uu.exe, uuaccelerator.exe)

## 使用方法

### 主界面

启动后会显示主窗口，包含：
- **状态栏**：显示程序运行状态（管理员权限）
- **拦截记录列表**：实时显示拦截操作
- **操作按钮**：
  - 手动检查 - 立即执行全面检查
  - 更新Hosts - 更新广告域名拦截规则
  - Hosts管理 - 备份/还原Hosts文件
  - 白名单 - 管理免拦截项目
  - 编辑规则 - 自定义拦截规则
  - 查看日志 - 查看历史拦截记录

### 系统托盘

点击【最小化到托盘】按钮：
- 程序隐藏到系统托盘
- 左键单击托盘图标显示主窗口
- 右键菜单可快速操作

## 测试拦截功能

### 测试1：安装进程秒杀

1. 复制任意exe文件
2. 重命名为 `360setup.exe` 或 `ludashi.exe`
3. 双击运行
4. **预期结果**：程序立即被杀死，显示"安装秒杀"

### 测试2：进程拦截

1. 复制任意exe文件
2. 重命名为 `360se.exe`
3. 双击运行
4. **预期结果**：主窗口显示"终止进程：360se.exe"

### 测试3：Hosts拦截

1. 点击主界面【更新Hosts】
2. 打开浏览器访问 `2345.com`
3. **预期结果**：无法访问（被Hosts拦截）

### 测试4：白名单保护

1. 复制任意exe文件
2. 重命名为 `steam.exe`
3. 双击运行
4. **预期结果**：程序正常运行，不被拦截

## 支持的拦截目标

### 已内置支持

- **鲁大师系列** - 鲁大师主程序、游戏助手等
- **360系列** - 360安全卫士、360浏览器、360杀毒等
- **2345系列** - 2345浏览器、2345看图王、2345好压等
- **金山系列** - 毒霸、金山卫士等
- **QQ电脑管家** - qqpcmgr等

### 内置广告域名

包含60+广告服务器域名

## 配置文件说明

配置文件位于 `config\config.json`：

```json
{
  "software_list": {
    "block_processes": ["进程名.exe"],
    "install_killers": ["安装程序关键词"]
  },
  "whitelist": {
    "processes": ["白名单进程.exe"],
    "domains": ["白名单域名.com"]
  },
  "ad_servers": ["0.0.0.0 域名.com"],
  "settings": {
    "check_interval": 2
  }
}
```

## 常见问题

### Q1: 提示"未检测到Python环境"

**A**: 
1. 访问 https://www.python.org/downloads/ 下载Python
2. 安装时务必勾选 **"Add Python to PATH"**
3. 安装完成后重新运行

### Q2: 程序无法获取管理员权限

**A**:
1. 确保系统UAC没有关闭
2. 右键点击程序，选择"以管理员身份运行"
3. 检查杀毒软件是否阻止提权

### Q3: Hosts更新失败

**A**:
1. 确保程序已获取管理员权限
2. 检查杀毒软件是否保护Hosts文件

### Q4: 误拦截了正常软件

**A**:
1. 点击【白名单】按钮
2. 将误拦截的软件添加到白名单
3. 保存后重启程序

### Q5: 如何彻底卸载拦截的软件

**A**:
1. 先运行本程序阻止其自保护
2. 使用系统自带的卸载程序卸载
3. 运行CCleaner等工具清理残留

## 技术原理

### 强制管理员提权
```python
ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, ...)
```

### 安装进程秒杀
- 检测进程名是否包含安装关键词
- 发现后立即调用 `kill()` 强制终止
- 同时删除安装文件

### 白名单保护
- 进程启动前检查白名单
- 白名单中的进程直接放行
- 不误杀正常软件

## 依赖包

| 包名 | 版本 | 用途 |
|------|------|------|
| psutil | >=5.9.0 | 进程监控 |
| watchdog | >=3.0.0 | 文件监控 |
| pystray | >=0.19.0 | 系统托盘 |
| pillow | >=9.0.0 | 托盘图标 |

## 更新日志

### v2.0 (2026-4-27)
- 新增强制管理员提权功能
- 新增安装进程秒杀功能
- 新增白名单保护机制
- 保护360急救箱、Steam、GitHub、火绒、UU加速器
- 保留全部原有功能

### v1.1 (2026-4-25)
- 新增Hosts自动备份与一键还原
- 新增域名白名单机制
- 新增智能规则校验

### v1.0 (2026-3-12)
- 初始版本发布

## 免责声明

本软件仅供学习研究使用，请勿用于非法用途。使用本软件造成的任何后果由用户自行承担。

---
© 2024 Alaswint. All rights reserved.
本项目采用 CC BY-NC-SA 4.0 协议开源，严格禁止任何形式的商用、售卖、盈利

**如果觉得本项目对你有帮助，请给个 Star
## 开源协议声明
版权说明 / Copyright
版权所有 © 2026 Alaswint
保留所有权利。
开源协议 / License
本项目采用 GNU 通用公共许可证第 3 版 进行许可。
简单来说：你可以自由地使用、修改和分发本软件（包括商业用途），但必须遵守以下核心条款：
1.	开源义务：如果你分发基于本项目的修改版本或衍生作品，你必须公开你的源代码。
2.	传染性：你的衍生作品也必须采用 GPLv3（或兼容）协议进行授权。
3.	免责声明：本软件按"原样"提供，不提供任何明示或暗示的担保。
This project is licensed under the GNU General Public License v3.0.
Permissions:
•	Commercial use
•	Modification
•	Distribution
•	Patent use
•	Private use
Limitations:
•	Liability
•	Trademark use
•	Must disclose source code (Copyleft)
You can find the full text of the license below or at https://www.gnu.org/licenses/gpl-3.0.html.
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007
Copyright (C) 2007 Free Software Foundation, Inc. https://fsf.org/Everyone is permitted to copy and distribute verbatim copiesof this license document, but changing it is not allowed.
Preamble
The GNU General Public License is a free, copyleft license forsoftware and other kinds of works.
The licenses for most software and other practical works are designedto take away your freedom to share and change the works.  By contrast,the GNU General Public License is intended to guarantee your freedom toshare and change all versions of a program--to make sure it remains freesoftware for all its users.  We, the Free Software Foundation, use theGNU General Public License for most of our software; it applies also toany other work released this way by its authors.  You can apply it toyour programs, too.
When we speak of free software, we are referring to freedom, notprice.  Our General Public Licenses are designed to make sure that youhave the freedom to distribute copies of free software (and charge forthem if you wish), that you receive source code or can get it if youwant it, that you can change the software or use pieces of it in newfree programs, and that you know you can do these things.
To protect your rights, we need to prevent others from denying youthese rights or asking you to surrender the rights.  Therefore, you havecertain responsibilities if you distribute copies of the software, or ifyou modify it: responsibilities to respect the freedom of others.
For example, if you distribute copies of such a program, whethergratis or for a fee, you must pass on to the recipients the samefreedoms that you received.  You must make sure that they, too, receiveor can get the source code.  And you must show them these terms so theyknow their rights.
Developers that use the GNU GPL protect your rights with two steps:(1) assert copyright on the program, and (2) offer you this Licensegiving you legal permission to copy, distribute and/or modify it.
For the developers' and authors' protection, the GPL clearly explainsthat there is no warranty for this free software.  For both users' andauthors' sake, the GPL requires that modified versions be marked aschanged, so that their problems will not be attributed erroneously toauthors of previous versions.
Some devices are designed to deny users access to install or runmodified versions of the software inside them, although the manufacturercan do so.  This is fundamentally incompatible with the aim ofprotecting users' freedom to change the software.  The systematicpattern of such abuse occurs in the area of products for individuals touse, which is precisely where it is most unacceptable.  Therefore, wehave designed this version of the GPL to prohibit the practice for thoseproducts.  If such problems arise substantially in other domains, westand ready to extend this provision to those domains in future versionsof the GPL, as needed to protect the freedom of users.
Finally, every program is threatened constantly by software patents.States should not allow patents to restrict development and use ofsoftware on general-purpose computers, but in those that do, we wish toavoid the special danger that patents applied to a free program couldmake it effectively proprietary.  To prevent this, the GPL assures thatpatents cannot be used to render the program non-free.
The precise terms and conditions for copying, distribution andmodification follow.
TERMS AND CONDITIONS
0. Definitions.
"This License" refers to version 3 of the GNU General Public License.
"The Program" refers to any copyrightable work licensed under thisLicense.  Each licensee is addressed as "you".  "Licensees" and"recipients" may be individuals or organizations.
To "modify" a work means to copy from or adapt all or part of the workin a fashion requiring copyright permission, other than the making of anexact copy.  The resulting work is called a "modified version" of theearlier work or a work "based on" the earlier work.
A "covered work" means either the unmodified Program or a work basedon the Program.
To "propagate" a work means to do anything with it that, withoutpermission, would make you directly or secondarily liable forinfringement under applicable copyright law, except executing it on acomputer or modifying a private copy.  Propagation includes copying,distribution (with or without modification), making available to thepublic, and in some countries other activities as well.
To "convey" a work means any kind of propagation that enables otherparties to make or receive copies.  Mere interaction with a user througha computer network, with no transfer of a copy, is not conveying.
An interactive user interface displays "Appropriate Legal Notices"to the extent that it includes a convenient and prominently visiblefeature that (1) displays an appropriate copyright notice, and (2)tells the user that there is no warranty for the work (except to theextent that warranties are provided), that licensees may convey thework under this License, and how to view a copy of this License.  Ifthe interface presents a list of user commands or options, such as amenu, a prominent item in the list meets this criterion.
1. Source Code.
The "source code" for a work means the preferred form of the workfor making modifications to it.  "Object code" means any non-sourceform of a work.
A "Standard Interface" means an interface that either is an officialstandard defined by a recognized standards body, or, in the case ofinterfaces specified for a particular programming language, one thatis widely used among developers working in that language.
The "System Libraries" of an executable work include anything, otherthan the work as a whole, that (a) is included in the normal form ofpackaging a Major Component, but which is not part of that MajorComponent, and (b) serves only to enable use of the work with thatMajor Component, or to implement a Standard Interface for which animplementation is available to the public in source code form.  A"Major Component", in this context, means a major essential component(kernel, window system, and so on) of the specific operating system(if any) on which the executable work runs, or a compiler used toproduce the work, or an object code interpreter used to run it.
The "Corresponding Source" for a work in object code form means allthe source code needed to generate, install, and (for an executablework) run the object code and to modify the work, including scripts tocontrol those activities.  However, it does not include the work'sSystem Libraries, or general-purpose tools or generally available freeprograms which are used unmodified in performing those activities butwhich are not part of the work.  For example, Corresponding Sourceincludes interface definition files associated with source files forthe work, and the source code for shared libraries and dynamicallylinked subprograms that the work is specifically designed to require,such as by intimate data communication or control flow between thosesubprograms and other parts of the work.
The Corresponding Source need not include anything that userscan regenerate automatically from other parts of the CorrespondingSource.
The Corresponding Source for a work in source code form is thatsame work.
2. Basic Permissions.
All rights granted under this License are granted for the term ofcopyright on the Program, and are irrevocable provided the statedconditions are met.  This License explicitly affirms your unlimitedpermission to run the unmodified Program.  The output from running acovered work is covered by this License only if the output, given itscontent, constitutes a covered work.  This License acknowledges yourrights of fair use or other equivalent, as provided by copyright law.
You may make, run and propagate covered works that you do notconvey, without conditions so long as your license otherwise remainsin force.  You may convey covered works to others for the sole purposeof having them make modifications exclusively for you, or provide youwith facilities for running those works, provided that you comply withthe terms of this License in conveying all material for which you donot control copyright.  Those thus making or running the covered worksfor you must do so exclusively on your behalf, under your directionand control, on terms that prohibit them from making any copies ofyour copyrighted material outside their relationship with you.
Conveying under any other circumstances is permitted solely underthe conditions stated below.  Sublicensing is not allowed; section 10makes it unnecessary.
3. Protecting Users' Legal Rights From Anti-Circumvention Law.
No covered work shall be deemed part of an effective technologicalmeasure under any applicable law fulfilling obligations under article11 of the WIPO copyright treaty adopted on 20 December 1996, orsimilar laws prohibiting or restricting circumvention of suchmeasures.
When you convey a covered work, you waive any legal power to forbidcircumvention of technological measures to the extent such circumventionis effected by exercising rights under this License with respect tothe covered work, and you disclaim any intention to limit operation ormodification of the work as a means of enforcing, against the work'susers, your or third parties' legal rights to forbid circumvention oftechnological measures.
4. Conveying Verbatim Copies.
You may convey verbatim copies of the Program's source code as youreceive it, in any medium, provided that you conspicuously andappropriately publish on each copy an appropriate copyright notice;keep intact all notices stating that this License and anynon-permissive terms added in accord with section 7 apply to the code;keep intact all notices of the absence of any warranty; and give allrecipients a copy of this License along with the Program.
You may charge any price or no price for each copy that you convey,and you may offer support or warranty protection for a fee.
5. Conveying Modified Source Versions.
You may convey a work based on the Program, or the modifications toproduce it from the Program, in the form of source code under theterms of section 4, provided that you also meet all of these conditions:
A compilation of a covered work with other separate and independentworks, which are not by their nature extensions of the covered work,and which are not combined with it such as to form a larger program,in or on a volume of a storage or distribution medium, is called an"aggregate" if the compilation and its resulting copyright are notused to limit the access or legal rights of the compilation's usersbeyond what the individual works permit.  Inclusion of a covered workin an aggregate does not cause this License to apply to the otherparts of the aggregate.
6. Conveying Non-Source Forms.
You may convey a covered work in object code form under the termsof sections 4 and 5, provided that you also convey themachine-readable Corresponding Source under the terms of this License,in one of these ways:
A separable portion of the object code, whose source code is excludedfrom the Corresponding Source as a System Library, need not beincluded in conveying the object code work.
A "User Product" is either (1) a "consumer product", which means anytangible personal property which is normally used for personal, family,or household purposes, or (2) anything designed or sold for incorporationinto a dwelling.  In determining whether a product is a consumer product,doubtful cases shall be resolved in favor of coverage.  For a particularproduct received by a particular user, "normally used" refers to atypical or common use of that class of product, regardless of the statusof the particular user or of the way in which the particular useractually uses, or expects or is expected to use, the product.  A productis a consumer product regardless of whether the product has substantialcommercial, industrial or non-consumer uses, unless such uses representthe only significant mode of use of the product.
"Installation Information" for a User Product means any methods,procedures, authorization keys, or other information required to installand execute modified versions of a covered work in that User Product froma modified version of its Corresponding Source.  The information mustsuffice to ensure that the continued functioning of the modified objectcode is in no case prevented or interfered with solely becausemodification has been made.
If you convey an object code work under this section in, or with, orspecifically for use in, a User Product, and the conveying occurs aspart of a transaction in which the right of possession and use of theUser Product is transferred to the recipient in perpetuity or for afixed term (regardless of how the transaction is characterized), theCorresponding Source conveyed under this section must be accompaniedby the Installation Information.  But this requirement does not applyif neither you nor any third party retains the ability to installmodified object code on the User Product (for example, the work hasbeen installed in ROM).
The requirement to provide Installation Information does not include arequirement to continue to provide support service, warranty, or updatesfor a work that has been modified or installed by the recipient, or forthe User Product in which it has been modified or installed.  Access to anetwork may be denied when the modification itself materially andadversely affects the operation of the network or violates the rules andprotocols for communication across the network.
Corresponding Source conveyed, and Installation Information provided,in accord with this section must be in a format that is publiclydocumented (and with an implementation available to the public insource code form), and must require no special password or key forunpacking, reading or copying.
7. Additional Terms.
"Additional permissions" are terms that supplement the terms of thisLicense by making exceptions from one or more of its conditions.Additional permissions that are applicable to the entire Program shallbe treated as though they were included in this License, to the extentthat they are valid under applicable law.  If additional permissionsapply only to part of the Program, that part may be used separatelyunder those permissions, but the entire Program remains governed bythis License without regard to the additional permissions.
When you convey a copy of a covered work, you may at your optionremove any additional permissions from that copy, or from any part ofit.  (Additional permissions may be written to require their ownremoval in certain cases when you modify the work.)  You may placeadditional permissions on material, added by you to a covered work,for which you have or can give appropriate copyright permission.
Notwithstanding any other provision of this License, for material youadd to a covered work, you may (if authorized by the copyright holdersof that material) supplement the terms of this License with terms:
All other non-permissive additional terms are considered "furtherrestrictions" within the meaning of section 10.  If the Program as youreceived it, or any part of it, contains a notice stating that it isgoverned by this License along with a term that is a furtherrestriction, you may remove that term.  If a license document containsa further restriction but permits relicensing or conveying under thisLicense, you may add to a covered work material governed by the termsof that license document, provided that the further restriction doesnot survive such relicensing or conveying.
If you add terms to a covered work in accord with this section, youmust place, in the relevant source files, a statement of theadditional terms that apply to those files, or a notice indicatingwhere to find the applicable terms.
Additional terms, permissive or non-permissive, may be stated in theform of a separately written license, or stated as exceptions;the above requirements apply either way.
8. Termination.
You may not propagate or modify a covered work except as expresslyprovided under this License.  Any attempt otherwise to propagate ormodify it is void, and will automatically terminate your rights underthis License (including any patent licenses granted under the thirdparagraph of section 11).
However, if you cease all violation of this License, then yourlicense from a particular copyright holder is reinstated (a)provisionally, unless and until the copyright holder explicitly andfinally terminates your license, and (b) permanently, if the copyrightholder fails to notify you of the violation by some reasonable meansprior to 60 days after the cessation.
Moreover, your license from a particular copyright holder isreinstated permanently if the copyright holder notifies you of theviolation by some reasonable means, this is the first time you havereceived notice of violation of this License (for any
