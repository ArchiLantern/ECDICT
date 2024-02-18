import sqlite3
from numpy import dtype, isin
import pandas as pd 
from pyquery import PyQuery
concise_dict = r'.\concise-enhanced.db'
conn = sqlite3.connect(concise_dict)



def en_to_cn(word = 'concise'): 
    df1 = pd.read_sql(f"""select * from  mdx  where entry='{word.lower()}' """, con=conn) 
    df2 = pd.read_sql(f"""select * from  mdx  where entry='{word.capitalize()}' """, con=conn) 
    # 注：因为entry有索引，如果 写lower(entry)=..，会导致不走索引，查询变慢！
    if df1.shape[0]:
        doc = PyQuery(df1.paraphrase.iloc[0])
        return doc.text().split('\n') 
    elif df2.shape[0]:
        doc = PyQuery(df2.paraphrase.iloc[0])
        return doc.text().split('\n') 
    else:
        return [] 
    

def words_translate(word_list='concise'):
    """ 
    关键标注有四处：  https://github.com/skywind3000/ECDICT/wiki/%E7%AE%80%E6%98%8E%E8%8B%B1%E6%B1%89%E5%AD%97%E5%85%B8%E5%A2%9E%E5%BC%BA%E7%89%88 
        - 音标后面：K 代表是牛津3000核心词汇，2代表是柯林斯两星词。
        - 下面的衍生词：各类简明英汉词典都没有，我用 NodeBox + BNC 语料库分析生成的。
        - 考试大纲词汇标注，是否是四级词汇？考研词汇？
        - 大纲后面的词频标注：7131/8802 前面代表 COCA 词频（按COCA词频高低排序，第7131个单词），后面是 BNC词频。 
    """
    df_words = pd.DataFrame({'no': [], 'word': []})
    if len(word_list) > 0:
        if isinstance(word_list, str):
            df_words = pd.concat([df_words, pd.DataFrame({'no':[1], 'word': [word_list]})], axis=0)
        elif isinstance(word_list, (list, tuple)): 
            df = pd.DataFrame({'word': list(word_list)}).reset_index(names=['no'])
            df['no'] = df['no'] + 1
            df_words = pd.concat([df_words, df], axis=0)
            # print(df_words)
        elif isinstance(word_list, pd.DataFrame):
            df_words = pd.concat([df_words, word_list], axis=0)

        df_words = df_words.astype({'no': int})  
        df_words['phonetic'] = df_words.word.apply(lambda w: en_to_cn(w)[1] if en_to_cn(w) else None ) 
        df_words['cn'] = df_words.word.apply(lambda w: '; '.join(en_to_cn(w)[2:-1]).replace('时态', '\n时态') if en_to_cn(w) else None ) 
        df_words['kg_freq'] = df_words.word.apply(lambda w: en_to_cn(w)[-1] if en_to_cn(w) else None ) 

        return df_words



if __name__ == '__main__': 
    # word_list = ('concise', 'Yoga Pants', 'saint', 'Stygian')
    word_list = ['concise', 'Yoga Pants', 'saint', 'Stygian']
    words_df = pd.DataFrame({'word': list(word_list)}).reset_index(names=['no'])
    words_df['no'] = words_df['no'] + 1
    print(words_df) 
 
    print(words_translate())
    print(words_translate(word_list))
    print(words_translate(words_df))
