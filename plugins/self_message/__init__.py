'''
#### 插件类型 -- python包

#### 插件功能 -- 按条件发送信息

插件开发 注意事项
--------------
 - 插件类都必须是 `Plugin` 类的子类，并必须实现 `rule()` 和 `handle()` 方法
 - 在插件类代码中包含两个重要属性
   - `priority`属性表示插件的优先级，数字越小表示优先级越高
   - `block`属性表示在当前插件执行完成后是否继续事件的传播，若值为True则比当前插件优先级低的插件都不会被执行
 - 插件工作原理：协议适配器产生一个事件（例如收到一条信息），会按照优先级分发事件给各个插件的`rule()`方法，根据返回值判断是否执行`handle()`方法


Base Explain::

    from alicebot import Plugin
    
    class TestPlugin(Plugin):
        priority: int = 0
        block: bool = False
    
        async def handle(self) -> None:
            pass
        
        async def rule(self) -> bool:
            return True

常用表情索引对照表
---------------
 -   0:惊讶
 -   1:撇嘴
 -   2:色
 -   5:流泪
 -   7:闭嘴
 -  11:愤怒
 -  18:大喊
 -  36:衰
 -  76:强
 -  96:害羞
 - 106:委屈
 - 109:亲亲
 - 111:可怜
 - 112:菜刀
 - 118:抱拳
 - 174:摊手
 - 175:卖萌
 - 226:拍桌
 - 
'''