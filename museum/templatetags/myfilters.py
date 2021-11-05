from django import template # 追記 必須
register = template.Library() # 追記 必須

@register.filter() # デコレータをつける
def removecolon(value):
    s = str(value)
    return int(s[0:2]+s[3:5])