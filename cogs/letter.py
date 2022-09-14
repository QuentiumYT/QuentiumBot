import nextcord, json, re
from nextcord.ext import commands
from QuentiumBot import storage, get_translations

# Basic command configs
cmd_name = "letter"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

with open("data/letters_dict.json", "r", encoding="utf-8", errors="ignore") as file:
    letters = json.loads(file.read(), strict=False)

class LetterUtilities(commands.Cog):
    """Letter command in Utilities section"""

    def __init__(self, client):
        self.client = client

    # Function to turn a text emoji into its object
    def emo(self, text):
        return str(nextcord.utils.get(self.client.emojis, name=text))

    # Function to cut a string of the specified length to a list
    def truncate(self, s, n):
        return [s[i:i + n] for i in range(0, len(s), n)]

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    async def letter_cmd(self, ctx, *, args=None):
        # Get specific server data
        if isinstance(ctx.channel, nextcord.TextChannel):
            data = await storage.retrieve_data(ctx.message.guild)
            lang_server = data[0]
        else:
            lang_server = "en"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            # No args given
            if not args:
                return await ctx.send(cmd_tran["msg_specify_text"])

            lst = []
            # Find emojis in given args
            emojis_used = re.findall(r"<\w*:\w*:\d*>", args)
            emojis_temp = []
            if emojis_used:
                for emoji in emojis_used:
                    # Replace nitro emojis if the bot doesn't know them
                    if int(emoji.split(":", 2)[2].split(">")[0]) in [x.id for x in self.client.emojis]:
                        args = args.replace(emoji, "☺") # Custom emoji
                    else:
                        args = args.replace(emoji, "☻") # Unrecognized emoji (nitro)
                        emojis_temp.append(emoji)
            # Remove unrecognized emojis
            for emojis in emojis_temp:
                emojis_used.remove(emojis)
            # Find a user mention, keeps it without turning into letters
            is_mention = re.findall(r"<@\d*>", args)
            for mention in is_mention:
                args = args.replace(mention, str(nextcord.utils.get(self.client.get_all_members(), id=int(mention[2:-1])).name))
            # List letters and lower
            letter = list(str(args.lower()))
            for char in range(len(letter)):
                # If ASCII chars used not in discord emojis
                if any(x == letter[char] for x in letters.keys()):
                    # Using my characters emojis
                    if "emo(" in letters[letter[char]]:
                        lst += self.emo(letters[letter[char]].replace("emo(", "")[0:-1])
                    else:
                        lst += letters[letter[char]]
                # Languages char variants
                elif any(x in letter[char] for x in ["â", "ä", "à", "å"]):
                    lst += ":regional_indicator_a:"
                elif any(x in letter[char] for x in ["ê", "ë", "è", "é"]):
                    lst += ":regional_indicator_e:"
                elif any(x in letter[char] for x in ["î", "ï", "ì", "í"]):
                    lst += ":regional_indicator_i:"
                elif any(x in letter[char] for x in ["ô", "ö", "ò", "ó"]):
                    lst += ":regional_indicator_o:"
                elif any(x in letter[char] for x in ["û", "ü", "ù", "ú"]):
                    lst += ":regional_indicator_u:"
                # Normal alphabet
                elif letter[char].isalpha():
                    lst += ":regional_indicator_" + letter[char] + ":"
                # If the char is an known emoji, replace it back here
                elif letter[char] == "☺":
                    lst.append(str(emojis_used[0]))
                    del emojis_used[0]
                else:
                    lst.append(letter[char])

            # Join list of every emojis
            content = "".join(lst)
            # Custom function to group string to a list of length of 2020
            embeds_temp = self.truncate(content, 2020)
            embeds = []
            cut_end_embed = ""
            # Custom emojis might be split in half, fixing it
            for x in embeds_temp:
                full_embed = re.split(r"(<\w+:\w+:\d+>|:\w+:)", cut_end_embed + x)[:-1]
                embeds.append("".join(full_embed))
                cut_end_embed = re.split(r"(<\w+:\w+:\d+>|:\w+:)", x)[-1:][0]
            # Add cut string to last embed
            embeds[-1] = embeds[-1] + "".join(cut_end_embed)
            # For each list of characters, send an embed
            for new_embed in embeds:
                embed = nextcord.Embed(color=0xFFA952)
                embed.description = new_embed
                # If last embed, add a footer
                if new_embed == embeds[-1]:
                    embed.set_footer(text=tran["GLOBAL"][lang_server]["requested_by"].format(ctx.message.author.name),
                                     icon_url=ctx.message.author.avatar)
                await ctx.send(embed=embed)

def setup(client):
    client.add_cog(LetterUtilities(client))
