from typing import Dict

SERVER='http://192.168.200.135:8000'
NER='/ner/predict/'
CLASSIFY='/classify/predict/'
SUMMARIZE = '/summarization/predict/'
DIALECT_DECT='/dialect_detection/predict/'
LANG_DECT='/language_detection/predict/'
SENTIMENT_ANALYSIS='/sentiment_analysis/predict/'
TRANSLATE='/translation/predict/'
CLASSIFY_IN_CLASS='عسكري-قضاء-امني-اقتصادي-اجتماعي-دين-سياسي'
#CLASSIFY_IN_CLASS='جيش عسكر حرب-قضاء تحقيق أمن-مال إقتصاد-سياسة أحزاب-دين-تكنولوجيا-صحة بيئة طب-رياضة-ثقافة فن'
TRANSLATE_IN_LANGUAGE='en-ar'

#عسكري-قضاء-امني-اقتصادي-اجتماعي-دين-سياسي-دولي
NER_LABELS={'job':'وظيفة' , 'event':'حَدث' , 'creativework':'عمل إبداعي' , 'organization':'مُنظمة'  , 'location':'مكان' ,
            'nationality':'جنسية' , 'product':'مُنتج' , 'artwork':'عمل فني' , 'person':'شخص' , 'time':'توقيت' }

CLASSIFY_LABELS={'military':'عسكري' , 'investigation':'قضاء' , 'economy':'اقتصادي' , 'politic':'سياسي' , 'relegion':'دين' ,'security':'امني' ,'social':'اجتماعي'}






sentimentLabels='"id2label": {    "إيجابي": "positive",    "سلبي": "negative",    "حيادي": "neutral"}'

