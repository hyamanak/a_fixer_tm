import re, jaconv, json, datetime
from bs4 import BeautifulSoup


han_zen = '[A-Za-z0-9:?!|%$#\)][ぁ-んァ-ンー-龥]'
zen_han = '[ぁ-んァ-ンー-龥][A-Za-z0-9?!%$#|\(]'
hankaku = '[A-Za-z0-9!?@#$%^*:]'
jp_char = '[あ-んア-ンー-龥]'
zenkaku_non_jp_chars = '[Ａ-Ｚａ-ｚ０-９：！？＋＊＆＾％＄＃＠”；＞＜／｛｝［］　]'
jp_parenthesis = '[「」『』]'

def if_jp_seg(line):
    return bool(re.search(jp_char, line))

def get_space_error_list(line):
    return re.findall(zen_han, line) + re.findall(han_zen, line)

def if_space_isss(line):
    return bool(re.search(han_zen, line) or re.search(zen_han, line))

def get_space_issues(line):
    return re.findall(zen_han, line) + re.findall(han_zen, line) 
    #returns a list of issues (#error list)

def add_space(error_list):
    new_list = []
    for item in error_list:
        new_list.append(item[0] + ' ' + item[1])
    return new_list
    #return fixed list

def fix_space_issues(fixed_list, error_list, line):
    for fixed_item, error_item in zip(fixed_list, error_list):
        line = line.replace(error_item, fixed_item)
    return line #retunr line with fixed space
    
def check_tag_space(line, ids):
    def add_tag_space(error_list, type):
        new_list = []
        if type == "open":
            for item in error_list:
                new_list.append(item[0] + ' ' + item[1:])
        if type == "close":
            for item in error_list:
                new_list.append(item[:-1] + ' ' + item[-1])
        
        return new_list
    

   
    
    opentag_space_issues = []
    closetag_space_issues = []
    
    error_list = []
    fixed_list = []

    fixed_opentag_list = []
    fixed_closetag_list = []

    for an_id in ids:
        open_tag = '<bpt i="' + an_id + '" x="' + an_id + '"\/>'
        close_tag = '<ept i="' + an_id + '"\/>'
        open_tag_space = jp_char + open_tag
        close_tag_space = close_tag + jp_char
        #print(an_id)
        
        #print(open_tag_space, close_tag_space, line)
        #print(bool(re.search(open_tag_space, line)))

        if bool(re.search(open_tag_space, line)):
            opentag_space_issues = re.findall(open_tag_space, line)
            #print(opentag_space_issues)
            fixed_opentag_list = add_tag_space(opentag_space_issues, "open")
            #print(opentag_space_issues)

            ##ex. ああ<XXX>アドレス</XXX> ['あ＜']
        if bool(re.search(close_tag_space, line)):
            closetag_space_issues = re.findall(close_tag_space, line)
            fixed_closetag_list = add_tag_space(closetag_space_issues, "close")
            #print(closetag_space_issues)

        if len(opentag_space_issues) != 0 or len(closetag_space_issues) !=0: 
            error_list = opentag_space_issues + closetag_space_issues
            fixed_list = fixed_opentag_list + fixed_closetag_list
            
            #print(error_list)
            line = fix_space_issues(fixed_list, error_list, line)
            #print(line, file=output)

    if len(error_list) == 0:
        return False

    return line


def if_byte_issues(line):
    return bool(re.search(zenkaku_non_jp_chars, line))

def fix_byte_issues(line):
    return jaconv.z2h(line, ascii=True, kana=False, digit=True)
    #returns fixed whole chars to regular ones

def if_jp_parenthesis(line):
    return bool(re.search(jp_parenthesis, line))

def del_jp_parenthesis(line):
    return re.sub(jp_parenthesis, '', line)
    

def if_tuv(line):
    return '<tuv xml:lang="' in line

def check_lang(line):
    if 'xml:lang="en-us"' in line:
        lang = "en-us"
    elif 'xml:lang="ja' in line:
        lang = "ja"
    return lang

def if_link(line):
    return '"type":"link"' in line

def get_link_ids(linkdata):
    ids = []
    for link in formatted_linkdata:
        if link['type'] == "link":
            ids.append(link['id'])
    return ids

def mistranslate_dict(mistranslate): #create a dict from mistranslation list file, {'right':'wrong'} format
    mistranslate_dict = {}
    for item in mistranslate:
        wrong, right = item.split(',')
        mistranslate_dict[wrong] = right
    return mistranslate_dict #ex. {'サフィックス': '接尾辞'}


def if_mistranslate(line, mistranslate_dict):
    wrong_list = []
    for item in mistranslate_dict.keys():
        if item in line:
            wrong_list.append(item)
    
    if len(wrong_list) != 0:
        return wrong_list
    else:
        return False

def fix_mistranslate(line, mistranslate_dict, wrong_list):
    #print(wrong_list)
    for item in wrong_list:
        line = line.replace(item, mistranslate_dict[item])
    return line

def if_cho_on_prob(line):
    final_list = []
    for item in cho_ons:
        pattern = item[:-1]
        anyword = '.'
        matched_words = re.findall(pattern+anyword, line)
        if len(matched_words) != 0:
            for word in matched_words:
                if word[-1] != "ー":
                    final_list.append(word)
    #print(final_list)
    if len(final_list) != 0:
        return final_list
    else:
        return False

def fix_cho_on(line, cho_on_list):
    for list_item in cho_on_list:
        if list_item[-1] == "<":
            line = line.replace(list_item, list_item[:-1] + "ー" + "<")
        elif list_item[-1] == line[len(line)-len(list_item):]:
            line = line + 'ー'
        else:
            line = line.replace(list_item, list_item[:-1] + "ー" + list_item[-1])
    return line

with open('fuse.tmx', 'r') as input, open('output.tmx', 'a+') as output, open('cho_on.txt', 'r') as cho_on, open('mistranslation.txt', 'r') as mistranslate:
    segment_id = 0
    mod_segment_list = []

    cho_ons = cho_on.read().splitlines()
    mistranslate = mistranslate.read().splitlines()
    mistranslate_dict = mistranslate_dict(mistranslate)
    
    elements = []
    link_exist = False
    lang = "en-us"

    for line in input:
        if '<tuv xml:lang="ja"' in line:
            lang = "ja"
            segment_id += 1
            

        if '<tuv xml:lang="en-us"' in line:
            lang = "en-us"
            link_exist = False
            

        if lang == "ja" and '<prop type="mdata">' in line:
            if if_link(line):
                link_data = re.search('<prop type=\"mdata\">(.*?)<\/prop>', line).group(1)
                #print(link_data, file=output)
                formatted_linkdata = json.loads(link_data)
                ids = get_link_ids(formatted_linkdata) #get list of ids which is for link
                link_exist = True

        if "<seg>" not in line:
            print(line, file=output, end='')

        # if '"type":"link"' in line:
        #     print(True)
            # mdata = line
            # print(re.search('<prop type=\"mdata\">(.*?)<\/prop>', mdata).group(1))
        
        else: 
            if  lang == "en-us": ##check if segment lang is en or not, if en then output to the output file
                print(line, file=output, end='')
            else:
                original_line = line #make a copy of original translated segment
                
                if if_jp_parenthesis(line):
                    line = del_jp_parenthesis(line)

                if link_exist:
                    #print(lang)
                    stag_space_issues = check_tag_space(line, ids)
                    if stag_space_issues:
                        #print(stag_space_issues)
                        line = stag_space_issues

                if if_byte_issues(line):
                    line = fix_byte_issues(line)
                
                ##fix mistranslate
                wrong_list = if_mistranslate(line, mistranslate_dict)
                #print(wrong_list)
                if wrong_list:
                    line = fix_mistranslate(line, mistranslate_dict, wrong_list)

                #fix cho_on problems
                cho_on_list = if_cho_on_prob(line)
                if cho_on_list:
                    line = fix_cho_on(line, cho_on_list)

                if if_space_isss(line):
                    error_list = get_space_issues(line)
                    fixed_list = add_space(error_list)
                    line = fix_space_issues(fixed_list, error_list, line)
                    
                
                if original_line != line:
                    mod_segment_list.append(segment_id)
                    print(line, file=output, end='')
                
                else:
                    print(line, file=output, end='')
            
    
time = '_fxr{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
id_open_tag = '<prop type="modified_by">'
id_close_tag = '</prop>'
#print(mod_segment_list)
with open("output.tmx", 'r') as read_output, open('output_mod_id.tmx', 'a+') as mod_output:
    mod_segment_list.sort()
    current_seg = 0
    for line in read_output:
        if '<tuv xml:lang="ja"' in line:
            current_seg += 1
            print(line, file=mod_output, end='')
        
        elif current_seg in mod_segment_list and id_open_tag in line:
            end_tag_idx = re.search(id_close_tag, line)
            end_tag_idx = end_tag_idx.start()
            line = line[:end_tag_idx] + time + id_close_tag
            print(line, file=mod_output)
        else:
            print(line, file=mod_output, end='')
  

            


             # print(item)
        # print("Modified", item.find(type="modified_by"))
    #
    # print(soup.find_all(type="modified_by"))