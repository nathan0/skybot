import re, fnmatch

from util import hook

@hook.sieve
def sieve_suite(bot, input, func, kind, args):
    if input.command == 'PRIVMSG' and \
       input.conn.conf.get('ignorebots', True) and \
       input.nick.lower()[-3:] == 'bot' and args.get('ignorebots', True):
            return None

    if kind == "command":
        if input.trigger in input.conn.conf.get('disabled_commands', []):
            return None

        ignored = input.conn.conf.get('ignored', [])
        if input.host in ignored or input.nick in ignored:
            return None

    fn = re.match(r'^plugins.(.+).py$', func._filename)
    disabled = input.conn.conf.get('disabled_plugins', [])
    if fn and fn.group(1).lower() in disabled:
        return None

    acls = input.conn.conf.get('acls', {})
    for acl in [acls.get(func.__name__), acls.get(input.chan), acls.get(input.conn.server)]:
        if acl is None:
            continue
        if 'deny-except' in acl:
            allowed_channels = map(unicode.lower, acl['deny-except'])
            if input.chan.lower() not in allowed_channels:
                return None
        if 'allow-except' in acl:
            denied_channels = map(unicode.lower, acl['allow-except'])
            if input.chan.lower() in denied_channels:
                return None
        if 'whitelist' in acl:
            if func.__name__ not in acl['whitelist']:
                return None
        if 'blacklist' in acl:
            if func.__name__ in acl['whitelist']:
                return None
        if 'blacklist-nicks' in acl:
            if input.nick.lower() in acl['blacklist-nicks']:
                return None

    admins = input.conn.conf.get('admins', [])
    user = "%s@%s"%(input.nick,input.host)
    input.admin = any(fnmatch.fnmatch(user, i) for i in admins) or any(user.endswith("@" + i) for i in admins)
    #input.admin = user in admins

    if args.get('adminonly', False):
        if not input.admin:
            return None

    return input
