import discord
from discord.ext import commands
import asyncio
from datetime import datetime

# إعدادات البوت
TOKEN = "MTM0OTc5ODA0MDY0NjU4MjM0Mw.GCL0z2.L_c4T6gXKDAh6HYv_V9NZq08kZ2iS8VHZbaFuw"
PREFIX = "#"
WARN_LIMIT = 3
PUNISHMENT_ROLE = 'مسجون'

# إنشاء البوت مع الصلاحيات اللازمة
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# قاعدة بيانات بسيطة لتخزين التحذيرات (في التطبيق الحقيقي استخدم قاعدة بيانات دائمة)
warnings = {}

@bot.event
async def on_ready():
    print(f'تم تسجيل دخول البوت: {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name=f"{PREFIX}help للمساعدة"))

# دالة للتحقق من الصلاحيات
def has_permission(ctx):
    # التحقق إذا كان المستخدم يملك صلاحية الأدمنستريتر
    if ctx.author.guild_permissions.administrator:
        return True
    return False

# دالة إرسال إيمبد عن طريقة استخدام الأمر
async def send_usage_embed(ctx, command, description, usage):
    embed = discord.Embed(
        title=f"استخدام الأمر: {PREFIX}{command}",
        description=description,
        color=discord.Color.blue()
    )
    embed.add_field(name="طريقة الاستخدام", value=usage)
    await ctx.send(embed=embed)

# أمر الحظر
@bot.command(name="ban")
async def ban_command(ctx, member: discord.Member = None, *, reason="لم يذكر سبب"):
    if not has_permission(ctx):
        return await ctx.send("ليس لديك صلاحية لاستخدام هذا الأمر.")
        
    if member is None:
        return await send_usage_embed(ctx, "ban", "لحظر عضو", f"{PREFIX}ban @العضو [السبب]")
        
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        return await ctx.send("لا يمكنك حظر شخص رتبته أعلى من رتبتك أو مساوية لها.")
        
    try:
        await member.ban(reason=reason)
        await ctx.send(f"تم حظر {member.mention} بسبب: {reason}")
    except discord.Forbidden:
        await ctx.send("ليس لدي صلاحيات كافية لحظر هذا العضو.")

# أمر إلغاء الحظر
@bot.command(name="unban")
async def unban_command(ctx, user_id=None, *, reason="لم يذكر سبب"):
    if not has_permission(ctx):
        return await ctx.send("ليس لديك صلاحية لاستخدام هذا الأمر.")
        
    if user_id is None:
        return await send_usage_embed(ctx, "unban", "لإلغاء حظر عضو", f"{PREFIX}unban معرف_العضو [السبب]")
    
    try:
        # محاولة تفسير user_id كمعرف رقمي
        user_id = int(user_id.strip("<@!>"))
    except ValueError:
        return await ctx.send("الرجاء إدخال معرف صحيح للعضو.")
    
    try:
        bans = await ctx.guild.bans()
        for ban_entry in bans:
            if ban_entry.user.id == user_id:
                await ctx.guild.unban(ban_entry.user, reason=reason)
                return await ctx.send(f"تم إلغاء حظر {ban_entry.user.name}#{ban_entry.user.discriminator}")
        
        await ctx.send("لم يتم العثور على هذا المستخدم في قائمة المحظورين.")
    except discord.Forbidden:
        await ctx.send("ليس لدي صلاحيات كافية لإلغاء الحظر.")

# أمر التايم اوت
@bot.command(name="time")
async def timeout_command(ctx, member: discord.Member = None, minutes: int = None, *, reason="لم يذكر سبب"):
    if not has_permission(ctx):
        return await ctx.send("ليس لديك صلاحية لاستخدام هذا الأمر.")
        
    if member is None or minutes is None:
        return await send_usage_embed(ctx, "time", "لإعطاء تايم اوت للعضو", f"{PREFIX}time @العضو المدة_بالدقائق [السبب]")
    
    if minutes <= 0:
        return await ctx.send("الرجاء تحديد وقت صحيح للتايم اوت.")
    
    try:
        # تحويل الدقائق إلى ثواني لمكتبة discord.py
        await member.timeout(duration=minutes * 60, reason=reason)
        await ctx.send(f"تم إعطاء {member.mention} تايم اوت لمدة {minutes} دقيقة بسبب: {reason}")
    except discord.Forbidden:
        await ctx.send("ليس لدي صلاحيات كافية لإعطاء تايم اوت لهذا العضو.")

# أمر إلغاء التايم اوت
@bot.command(name="untime")
async def remove_timeout_command(ctx, member: discord.Member = None):
    if not has_permission(ctx):
        return await ctx.send("ليس لديك صلاحية لاستخدام هذا الأمر.")
        
    if member is None:
        return await send_usage_embed(ctx, "untime", "لإلغاء التايم اوت عن العضو", f"{PREFIX}untime @العضو")
    
    try:
        await member.timeout(None, reason="إلغاء التايم اوت بواسطة " + ctx.author.name)
        await ctx.send(f"تم إلغاء التايم اوت عن {member.mention}")
    except discord.Forbidden:
        await ctx.send("ليس لدي صلاحيات كافية لإلغاء التايم اوت.")

# أمر الطرد
@bot.command(name="kick")
async def kick_command(ctx, member: discord.Member = None, *, reason="لم يذكر سبب"):
    if not has_permission(ctx):
        return await ctx.send("ليس لديك صلاحية لاستخدام هذا الأمر.")
        
    if member is None:
        return await send_usage_embed(ctx, "kick", "لطرد عضو", f"{PREFIX}kick @العضو [السبب]")
    
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        return await ctx.send("لا يمكنك طرد شخص رتبته أعلى من رتبتك أو مساوية لها.")
    
    try:
        await member.kick(reason=reason)
        await ctx.send(f"تم طرد {member.mention} بسبب: {reason}")
    except discord.Forbidden:
        await ctx.send("ليس لدي صلاحيات كافية لطرد هذا العضو.")

# أمر الميوت
@bot.command(name="mute")
async def mute_command(ctx, member: discord.Member = None, *, reason="لم يذكر سبب"):
    if not has_permission(ctx):
        return await ctx.send("ليس لديك صلاحية لاستخدام هذا الأمر.")
        
    if member is None:
        return await send_usage_embed(ctx, "mute", "لكتم العضو في الدردشة النصية", f"{PREFIX}mute @العضو [السبب]")
    
    # البحث عن رتبة الكتم أو إنشاؤها
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not mute_role:
        try:
            # إنشاء رتبة الكتم
            mute_role = await ctx.guild.create_role(name="Muted", reason="رتبة للأعضاء المكتومين")
            
            # تعيين صلاحيات الكتم في جميع قنوات النص
            for channel in ctx.guild.channels:
                if isinstance(channel, discord.TextChannel):
                    await channel.set_permissions(mute_role, send_messages=False, add_reactions=False)
        except discord.Forbidden:
            return await ctx.send("ليس لدي صلاحيات كافية لإنشاء رتبة الكتم.")
    
    try:
        await member.add_roles(mute_role, reason=reason)
        await ctx.send(f"تم كتم {member.mention} في الدردشة النصية. السبب: {reason}")
    except discord.Forbidden:
        await ctx.send("ليس لدي صلاحيات كافية لإضافة رتبة الكتم لهذا العضو.")

# أمر إلغاء الميوت
@bot.command(name="unmute")
async def unmute_command(ctx, member: discord.Member = None):
    if not has_permission(ctx):
        return await ctx.send("ليس لديك صلاحية لاستخدام هذا الأمر.")
        
    if member is None:
        return await send_usage_embed(ctx, "unmute", "لإلغاء كتم العضو في الدردشة النصية", f"{PREFIX}unmute @العضو")
    
    # البحث عن رتبة الكتم
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not mute_role:
        return await ctx.send("لم يتم العثور على رتبة الكتم في هذا السيرفر.")
    
    if mute_role not in member.roles:
        return await ctx.send("هذا العضو غير مكتوم حالياً.")
    
    try:
        await member.remove_roles(mute_role)
        await ctx.send(f"تم إلغاء كتم {member.mention} في الدردشة النصية.")
    except discord.Forbidden:
        await ctx.send("ليس لدي صلاحيات كافية لإزالة رتبة الكتم من هذا العضو.")

# أمر نقل عضو من روم صوتي إلى آخر
@bot.command(name="سحب")
async def move_command(ctx, member: discord.Member = None, *, channel_name = None):
    if not has_permission(ctx):
        return await ctx.send("ليس لديك صلاحية لاستخدام هذا الأمر.")
        
    if member is None or channel_name is None:
        return await send_usage_embed(ctx, "سحب", "لنقل عضو من روم صوتي إلى آخر", f"{PREFIX}سحب @العضو اسم_الروم_الصوتي")
    
    if not member.voice or not member.voice.channel:
        return await ctx.send("هذا العضو غير متصل بأي روم صوتي حالياً.")
    
    # البحث عن الروم الصوتي
    voice_channel = discord.utils.get(ctx.guild.voice_channels, name=channel_name)
    if not voice_channel:
        return await ctx.send("لم يتم العثور على الروم الصوتي المحدد.")
    
    try:
        await member.move_to(voice_channel)
        await ctx.send(f"تم نقل {member.mention} إلى روم {voice_channel.name}.")
    except discord.Forbidden:
        await ctx.send("ليس لدي صلاحيات كافية لنقل هذا العضو.")

# أمر قفل الروم
@bot.command(name="قفل")
async def lock_command(ctx, *, channel_name = None):
    if not has_permission(ctx):
        return await ctx.send("ليس لديك صلاحية لاستخدام هذا الأمر.")
    
    # تحديد القناة المستهدفة
    channel = ctx.channel
    if channel_name:
        target_channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)
        if target_channel:
            channel = target_channel
        else:
            return await ctx.send("لم يتم العثور على الروم المحدد.")
    
    try:
        # قفل القناة للدور الافتراضي (@everyone)
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(f"تم قفل روم {channel.mention}.")
    except discord.Forbidden:
        await ctx.send("ليس لدي صلاحيات كافية لقفل هذا الروم.")

# أمر فتح الروم
@bot.command(name="فتح")
async def unlock_command(ctx, *, channel_name = None):
    if not has_permission(ctx):
        return await ctx.send("ليس لديك صلاحية لاستخدام هذا الأمر.")
    
    # تحديد القناة المستهدفة
    channel = ctx.channel
    if channel_name:
        target_channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)
        if target_channel:
            channel = target_channel
        else:
            return await ctx.send("لم يتم العثور على الروم المحدد.")
    
    try:
        # إعادة الصلاحيات الافتراضية للدور الافتراضي (@everyone)
        await channel.set_permissions(ctx.guild.default_role, send_messages=None)
        await ctx.send(f"تم فتح روم {channel.mention}.")
    except discord.Forbidden:
        await ctx.send("ليس لدي صلاحيات كافية لفتح هذا الروم.")

# أمر تحذير عضو
@bot.command(name="warn")
async def warn_command(ctx, member: discord.Member = None, *, reason="لم يذكر سبب"):
    if not has_permission(ctx):
        return await ctx.send("ليس لديك صلاحية لاستخدام هذا الأمر.")
        
    if member is None:
        return await send_usage_embed(ctx, "warn", "لتحذير عضو", f"{PREFIX}warn @العضو [السبب]")
    
    # تهيئة قائمة التحذيرات للعضو إذا لم تكن موجودة
    if str(ctx.guild.id) not in warnings:
        warnings[str(ctx.guild.id)] = {}
    
    if str(member.id) not in warnings[str(ctx.guild.id)]:
        warnings[str(ctx.guild.id)][str(member.id)] = []
    
    # إضافة التحذير
    warnings[str(ctx.guild.id)][str(member.id)].append({
        "reason": reason,
        "moderator": ctx.author.name,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    warn_count = len(warnings[str(ctx.guild.id)][str(member.id)])
    await ctx.send(f"تم تحذير {member.mention} بسبب: {reason}. عدد التحذيرات: {warn_count}")
    
    # التحقق من وصول العضو إلى الحد الأقصى من التحذيرات
    if warn_count >= WARN_LIMIT:
        punishment_role = discord.utils.get(ctx.guild.roles, name=PUNISHMENT_ROLE)
        
        if not punishment_role:
            try:
                punishment_role = await ctx.guild.create_role(name=PUNISHMENT_ROLE, colour=discord.Colour.red())
            except discord.Forbidden:
                return await ctx.send("ليس لدي صلاحيات كافية لإنشاء رتبة العقوبة.")
        
        try:
            await member.add_roles(punishment_role)
            await ctx.send(f"{member.mention} وصل إلى الحد الأقصى من التحذيرات ({WARN_LIMIT}) وتم إعطاؤه رتبة {punishment_role.name}.")
        except discord.Forbidden:
            await ctx.send("ليس لدي صلاحيات كافية لإضافة رتبة العقوبة لهذا العضو.")

# أمر إزالة تحذير
@bot.command(name="unwarn")
async def unwarn_command(ctx, member: discord.Member = None, warn_number: int = None):
    if not has_permission(ctx):
        return await ctx.send("ليس لديك صلاحية لاستخدام هذا الأمر.")
        
    if member is None:
        return await send_usage_embed(ctx, "unwarn", "لإزالة تحذير من عضو", f"{PREFIX}unwarn @العضو [رقم_التحذير]")
    
    # التحقق من وجود تحذيرات للعضو
    guild_id = str(ctx.guild.id)
    member_id = str(member.id)
    
    if (guild_id not in warnings or 
        member_id not in warnings[guild_id] or 
        len(warnings[guild_id][member_id]) == 0):
        return await ctx.send(f"{member.mention} ليس لديه أي تحذيرات.")
    
    # إزالة تحذير محدد أو آخر تحذير
    user_warnings = warnings[guild_id][member_id]
    
    if warn_number is not None:
        if warn_number < 1 or warn_number > len(user_warnings):
            return await ctx.send("رقم التحذير غير صالح.")
        
        del user_warnings[warn_number - 1]
        await ctx.send(f"تم إزالة التحذير رقم {warn_number} من {member.mention}. عدد التحذيرات المتبقية: {len(user_warnings)}")
    else:
        user_warnings.pop()
        await ctx.send(f"تم إزالة آخر تحذير من {member.mention}. عدد التحذيرات المتبقية: {len(user_warnings)}")

# أمر عرض تحذيرات عضو
@bot.command(name="warns")
async def warns_command(ctx, member: discord.Member = None):
    if not has_permission(ctx):
        return await ctx.send("ليس لديك صلاحية لاستخدام هذا الأمر.")
        
    if member is None:
        return await send_usage_embed(ctx, "warns", "لعرض تحذيرات عضو", f"{PREFIX}warns @العضو")
    
    # التحقق من وجود تحذيرات للعضو
    guild_id = str(ctx.guild.id)
    member_id = str(member.id)
    
    if (guild_id not in warnings or 
        member_id not in warnings[guild_id] or 
        len(warnings[guild_id][member_id]) == 0):
        return await ctx.send(f"{member.mention} ليس لديه أي تحذيرات.")
    
    # إنشاء إيمبد لعرض التحذيرات
    user_warnings = warnings[guild_id][member_id]
    embed = discord.Embed(
        title=f"تحذيرات {member.name}",
        description=f"عدد التحذيرات: {len(user_warnings)}",
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    for i, warning in enumerate(user_warnings):
        embed.add_field(
            name=f"تحذير {i+1}",
            value=f"السبب: {warning['reason']}\nبواسطة: {warning['moderator']}\nالتاريخ: {warning['timestamp']}",
            inline=False
        )
    
    await ctx.send(embed=embed)

# أمر تغيير الاسم المستعار
@bot.command(name="nick")
async def nick_command(ctx, member: discord.Member = None, *, new_nickname = None):
    if not has_permission(ctx):
        return await ctx.send("ليس لديك صلاحية لاستخدام هذا الأمر.")
        
    if member is None:
        return await send_usage_embed(ctx, "nick", "لتغيير الاسم المستعار للعضو", f"{PREFIX}nick @العضو [الاسم_الجديد]")
    
    try:
        await member.edit(nick=new_nickname)
        if new_nickname:
            await ctx.send(f"تم تغيير الاسم المستعار لـ {member.mention} إلى \"{new_nickname}\".")
        else:
            await ctx.send(f"تم إعادة الاسم المستعار الأصلي لـ {member.mention}.")
    except discord.Forbidden:
        await ctx.send("ليس لدي صلاحيات كافية لتغيير الاسم المستعار لهذا العضو.")

# أمر إضافة/إزالة رتبة
@bot.command(name="رول")
async def role_command(ctx, member: discord.Member = None, *, role_name = None):
    if not has_permission(ctx):
        return await ctx.send("ليس لديك صلاحية لاستخدام هذا الأمر.")
        
    if member is None or role_name is None:
        return await send_usage_embed(ctx, "رول", "لإضافة أو إزالة رتبة من عضو", f"{PREFIX}رول @العضو اسم_الرتبة")
    
    # البحث عن الرتبة
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        return await ctx.send("لم يتم العثور على الرتبة المحددة.")
    
    try:
        if role in member.roles:
            # إزالة الرتبة إذا كان العضو يملكها بالفعل
            await member.remove_roles(role)
            await ctx.send(f"تم إزالة رتبة \"{role.name}\" من {member.mention}.")
        else:
            # إضافة الرتبة إذا لم يكن العضو يملكها
            await member.add_roles(role)
            await ctx.send(f"تم إضافة رتبة \"{role.name}\" إلى {member.mention}.")
    except discord.Forbidden:
        await ctx.send("ليس لدي صلاحيات كافية لإدارة الرتب لهذا العضو.")

# أمر مسح الرسائل
@bot.command(name="مسح")
async def clear_command(ctx, amount: int = 10, channel: discord.TextChannel = None):
    if not has_permission(ctx):
        return await ctx.send("ليس لديك صلاحية لاستخدام هذا الأمر.")
    
    if amount <= 0 or amount > 100:
        return await ctx.send("يمكنك فقط مسح ما بين 1 و 100 رسالة في المرة الواحدة.")
    
    # تحديد القناة المستهدفة
    target_channel = channel if channel else ctx.channel
    
    try:
        deleted = await target_channel.purge(limit=amount)
        confirm_msg = await ctx.send(f"تم مسح {len(deleted)} رسالة من روم {target_channel.mention}.")
        
        # حذف رسالة التأكيد بعد 3 ثوانٍ
        await asyncio.sleep(3)
        await confirm_msg.delete()
    except discord.Forbidden:
        await ctx.send("ليس لدي صلاحيات كافية لمسح الرسائل.")
    except discord.HTTPException:
        await ctx.send("حدث خطأ أثناء مسح الرسائل. تأكد من أن الرسائل ليست أقدم من 14 يوماً.")

# تشغيل البوت
bot.run('MTM0OTc5ODA0MDY0NjU4MjM0Mw.GCL0z2.L_c4T6gXKDAh6HYv_V9NZq08kZ2iS8VHZbaFuw')
