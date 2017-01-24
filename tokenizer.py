# -*- coding: UTF-8 -*-
"""
tokenizer.py
````````````
Functions and classes for tokenizing texts

EXAMPLE:

tokenizer = Tokenizer(
        add_stopwords = ["l","stat","pub"],

        use_lexical_smoothing  = True,        
        use_stemming           = True,
        use_pos_tagging        = True,
        use_standard_stopwords = True
);

"""
import sys

# Support locally-installed libraries
sys.path.append("./lib") 

import re       # Regular expressions used in tokenizer
import nltk     # Used for part-of-speech tagging 
import os       # Used to iterate files in from_directory()

###############################################################################
# TOKENIZER constants 
###############################################################################

# Ensure that the POS tagging database is available.
# nltk.download("averaged_perceptron_tagger");

# Tell NLTK where it can find the data for Part-of-speech tagging. 
#nltk.data.path.append("./extra/nltk_data/");

# English stopword list from Stone, Denis, Kwantes (2010)
STOPWORDS = """
a about above across after afterwards again against all almost alone along 
already also although always am among amongst amoungst amount an and another 
any anyhow anyone anything anyway anywhere are around as at back be became 
because become becomes becoming been before beforehand behind being below 
beside besides between beyond bill both bottom but by call can cannot cant co 
computer con could couldnt cry de describe detail did didn do does doesn doing 
don done down due during each eg eight either eleven else elsewhere empty 
enough etc even ever every everyone everything everywhere except few fifteen
fify fill find fire first five for former formerly forty found four from front 
full further get give go had has hasnt have he hence her here hereafter hereby 
herein hereupon hers herself him himself his how however hundred i ie if in inc 
indeed interest into is it its itself keep last latter latterly least less ltd
just kg km made make many may me meanwhile might mill mine more moreover most 
mostly move much must my myself name namely neither never nevertheless next 
nine no nobody none noone nor not nothing now nowhere of off often on once one 
only onto or other others otherwise our ours ourselves out over own part per
perhaps please put rather re quite rather really regarding same say see seem 
seemed seeming seems serious several she should show side since sincere six 
sixty so some somehow someone something sometime sometimes somewhere still such 
system take ten than that the their them themselves then thence there 
thereafter thereby therefore therein thereupon these they thick thin third this 
those though three through throughout thru thus to together too top toward 
towards twelve twenty two un under until up unless upon us used using various 
very very via was we well were what whatever when whence whenever where 
whereafter whereas whereby wherein whereupon wherever whether which while 
whither who whoever whole whom whose why will with within without would yet you
your yours yourself yourselves
"""
STOPWORDS = [w for w in STOPWORDS.split() if w];

###############################################################################
# Classes 
###############################################################################

class Tokenizer:
        """ 
        To enhance the fit of the topic models, various strategies
        can be used to filter out non-semantic noise from the texts
        being tokenized. 
        
        These are, in order of application:
         
        1.) Lexical filtering 
              a. All sequences of whitespace become a single space
              b. All non-ASCII and punctuation characters are removed
              c. All letters are made lowercase
       
        2.) Part-of-speech (POS) filtering 
              a. Words that are not nouns are removed
        
        3.) Stop word filtering 
              a. Tokens in NLTK English stop word list are removed. 
              b. Tokens in user-provided stop word list are removed.
               
        4.) Stemming
              a. Related words replaced with a common stem 
        """ 

        # Match all sequences of whitespace, "--", or pre-escaped \n and \t.
        match_whitespace = re.compile("(\s|--|\\\\n|\\\\t)+");

        # Disallow characters matching this regex (note [^...])
        match_disallowed = re.compile("[^a-zA-Z0-9-_@#%&=\$\*\+\|\s]+");

        # List of English stop words. May combine with user's (see __init__())
        stopwords = STOPWORDS;

        # Instantiate an object to run Porter's stemming algorithm
        stemmer = nltk.stem.porter.PorterStemmer();

        def filter_lexical(self, string):
                """ 
                Remove certain lexical features from the given string

                Arguments:
                        @self  : Tokenizer object (automatic)
                        @string: Input string to be manipulated
                Return: 
                        The smoothed string
                EXAMPLE:
                        "are  you\\nwell--sailor John?" => "are you well sailor john"
                """
                # Replace all whitespace sequences with single space
                string = self.match_whitespace.sub(" ", string);

                # Remove all undesirable characters from string
                string = self.match_disallowed.sub("", string);

                # Convert all letters to lowercase
                string = string.lower();

                return string;

        def filter_part_of_speech(self, tokens):
                """ 
                Remove certain parts of speech from the token list

                Arguments:
                        @self      : Tokenizer object (automatic)
                        @token_list: Input as an array of words 
                Return: 
                        Some subset of the token list
                EXAMPLE:
                        ["are","you","well","sailor","john"] => ["you","sailor","john"]
                """
                tagged = nltk.pos_tag(tokens);

                return [w[0] for w in tagged if w[1][0] == "N"];

        def filter_stopwords(self, token_list):
                """ 
                Remove stopwords from the token list.

                Arguments:
                        @self      : Tokenizer object (automatic)
                        @token_list: List of Unicode tokens 
                Return: 
                        Some subset of the tokenized_string 
                EXAMPLE:
                        ["you","sailor","john"] => ["sailor","john"]
                """
                return [tok for tok in token_list if not tok in self.stopwords];

        def filter_stem_tokens(self, token_list): 
                """ 
                Perform stemming on the provided token list

                Arguments:
                        @self      : Tokenizer object (automatic)
                        @token_list: List of Unicode tokens 
                Return: 
                        List of stemmed unicode tokens
                EXAMPLE:
                        ["sailor","john"] => ["sail","john"]
                """
                return [self.stemmer.stem(tok) for tok in token_list];

        def tokenize(self, string):
                """
                Convert a string into a token list

                Arguments:
                        @self  : Tokenizer object (automatic)
                        @string: Input string
                Return: 
                        Processed token list (array of strings)
                """
                if self.do_lex:
                        string = self.filter_lexical(string);

                tokens = string.split();

                if self.do_pos:
                        tokens = self.filter_part_of_speech(tokens);

                if self.do_stopwords:
                        tokens = self.filter_stopwords(tokens);

                if self.do_stem:
                        tokens = self.filter_stem_tokens(tokens);

                return tokens;

        def __init__(self, **kwargs):
                """
                Create a new Tokenizer object

                Arguments:
                        @self  : Tokenizer object (automatic)
                        @kwargs: Associative array of options
                Return: 
                        Nothing 
                Options:
                        (BOOL) use_lexical_smoothing 
                        (BOOL) use_standard_stopwords 
                        (BOOL) use_pos_tagging
                        (BOOL) use_stemming 
                        (ARRAY OF STRING or BOOL) use_stopwords 
                """

                self.do_lex       = kwargs.pop("use_lexical_smoothing", True);
                self.do_stopwords = kwargs.pop("use_standard_stopwords", True);
                self.do_pos       = kwargs.pop("use_pos_tagging", True);
                self.do_stem      = kwargs.pop("use_stemming", True);

                stopwords         = kwargs.pop("use_stopwords", True);

                if isinstance(stopwords, list):
                        self.stopwords += extra_stopwords;

                if isinstance(stopwords, bool):
                        self.do_stopwords = stopwords;


