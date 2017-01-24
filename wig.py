#!/usr/bin/env python

import sys

sys.path.append("./lib");

import nltk
import re
import os
import sqlite3
import getopt
import hashlib

import tokenizer 

import csv


def create_sqlite_database(meta_file, gram_file, sgram_file, database):

        conn = sqlite3.connect(database);

	c = conn.cursor()

	################################################# 
        # texts table
	################################################# 
	# Load CSV into it 
        meta_csv  = csv.reader(open(meta_file))
        meta_head = next(meta_csv);
        meta_type = next(meta_csv);
        meta_arr = [(r[0],r[1],r[2],r[3],r[4],r[5]) for r in meta_csv];

        field_spec = []; 
        field_form = []; 
        field_search_create = []; 
        field_search_insert = []; 

        for i, value in enumerate(meta_head):
                field_spec.append(value+" "+meta_type[i]);
                field_form.append("?");
                field_search_create.append("text_"+value);
                field_search_insert.append("texts."+value);

        # "id INTEGER, filename TEXT, ..."
        field_spec = ",".join(field_spec);
        # "id, filename, ..."
        field_list = ",".join(meta_head); 
        # "?,?,..." used for INSERT (see below)
        field_form = ",".join(field_form); 

        # fields used in the search table
        field_search_create = ",".join(field_search_create); 
        field_search_insert = ",".join(field_search_insert); 

        print("Creating texts")
        c.execute("CREATE TABLE texts ("+field_spec+")");

	#c.execute("""
                #CREATE TABLE texts (
                        #id       INTEGER, 
                        #filename TEXT, 
                        #year     INTEGER, 
                        #title    TEXT, 
                        #usid     INTEGER, 
                        #category TEXT
                #)
        #""");


        print("Populating texts")
	c.executemany("INSERT INTO texts ("+field_list+") VALUES ("+field_form+");", meta_arr);

	#c.executemany("""
                #INSERT INTO texts (
                        #id, 
                        #filename, 
                        #year, 
                        #title, 
                        #usid, 
                        #category
                #) VALUES (?,?,?,?,?,?);""", 
        #meta_arr);


	################################################# 
        # grams table 
	################################################# 
        print("Creating grams")
	c.execute("""
                CREATE TABLE grams (
                        id       INTEGER, 
                        text_id  INTEGER, 
                        freq     INTEGER, 
                        n        INTEGER, 
                        gram    TEXT
                )
        """);

	# Load CSV into it 
        gram_csv = csv.reader(open(gram_file))
        gram_arr = [(r[0],r[1],r[2],r[3],r[4]) for r in gram_csv];

        print("Populating grams")
	c.executemany("""
                INSERT INTO grams (
                        id, 
                        text_id, 
                        freq, 
                        n, 
                        gram
                ) VALUES (?,?,?,?,?);""", 
        gram_arr);


	################################################# 
        # sgrams table 
	################################################# 
        print("Creating sgrams")
	c.execute("""
                CREATE TABLE sgrams (
                        id       INTEGER, 
                        text_id  INTEGER, 
                        freq     INTEGER, 
                        n        INTEGER, 
                        gram    TEXT
                )
        """);

	# Load CSV into it 
        gram_csv = csv.reader(open(sgram_file));
        gram_arr = [(r[0],r[1],r[2],r[3],r[4]) for r in gram_csv];

        print("Populating sgrams")
	c.executemany("""
                INSERT INTO sgrams (
                        id, 
                        text_id, 
                        freq, 
                        n, 
                        gram
                ) VALUES (?,?,?,?,?);""", 
        gram_arr);

	################################################# 
        # gram_search table 
	################################################# 
        #print("Creating gram_search")
	#c.execute("""
                #CREATE VIRTUAL TABLE gram_search 
                #USING fts4 (
                        #id, 
                        #text_id, 
                        #text_year, 
                        #text_filename, 
                        #text_title,
                        #text_category,
                        #freq, 
                        #n, 
                        #gram
                #)
        #""")

        #print("Populating gram_search")
        #c.execute("""
                #INSERT INTO gram_search 
                #SELECT 
                        #grams.id, 
                        #texts.id, 
                        #texts.year, 
                        #texts.filename, 
                        #texts.title,
                        #texts.category,
                        #grams.freq, 
                        #grams.n, 
                        #grams.gram 
                #FROM grams 
                #JOIN texts ON grams.text_id = texts.id
        #""");

        print("Creating gram_search")
        c.execute("""
                CREATE VIRTUAL TABLE gram_search 
                USING fts4 (
                        id, 
                        """+field_search_create+"""
                        freq, 
                        n, 
                        gram
                )
        """)

        print("Populating gram_search")
        c.execute("""
                INSERT INTO gram_search 
                SELECT 
                        grams.id, 
                        """+field_search_insert+"""
                        grams.freq, 
                        grams.n, 
                        grams.gram 
                FROM grams 
                JOIN texts ON grams.text_id = texts.id
        """);

        ######################################################################## 
        ## sgram_search table 
        ######################################################################## 
        print("Creating sgram_search")
        c.execute("""
                CREATE VIRTUAL TABLE sgram_search 
                USING fts4 (
                        id, 
                        """+field_search_create+"""
                        freq, 
                        n, 
                        gram
                )
        """)

        print("Populating sgram_search")
        c.execute("""
                INSERT INTO sgram_search 
                SELECT 
                        sgrams.id, 
                        """+field_search_insert+"""
                        sgrams.freq, 
                        sgrams.n, 
                        sgrams.gram 
                FROM sgrams 
                JOIN texts ON sgrams.text_id = texts.id
        """);

        #print("Creating sgram_search")
	#c.execute("""
                #CREATE VIRTUAL TABLE sgram_search 
                #USING fts4 (
                        #id, 
                        #text_id, 
                        #text_year, 
                        #text_filename, 
                        #text_title,
                        #text_category,
                        #freq, 
                        #n, 
                        #gram
                #)
        #""")

        #print("Populating sgram_search")
        #c.execute("""
                #INSERT INTO sgram_search 
                #SELECT 
                        #sgrams.id, 
                        #texts.id, 
                        #texts.year, 
                        #texts.filename, 
                        #texts.title,
                        #texts.category,
                        #sgrams.freq, 
                        #sgrams.n, 
                        #sgrams.gram 
                #FROM sgrams 
                #JOIN texts ON sgrams.text_id = texts.id
        #""");

	# Save (commit) the changes
	conn.commit()

        conn.close();







def generate_grams(texts_directory, texts_meta_file, n_vector):

        ####################################################################### 
        # Configure a tokenizer for the raw grams 
        ####################################################################### 
        raw_tok = tokenizer.Tokenizer(
                use_stopwords          = False,
                use_lexical_smoothing  = True,        
                use_stemming           = False,
                use_pos_tagging        = False,
                use_standard_stopwords = False, 
        );

        ####################################################################### 
        # Configure a tokenizer for the smoothed grams 
        ####################################################################### 
        smooth_tok = tokenizer.Tokenizer(
                use_lexical_smoothing  = True,        
                use_stemming           = False,
                use_pos_tagging        = False,
                use_stopwords          = True,
                use_standard_stopwords = True, 
        );

        gram_id = 0;

        rgrams_csv = open("rgrams.csv", "w+");
        sgrams_csv = open("sgrams.csv", "w+");

        text_csv = csv.reader(open(texts_meta_file))

        for row in text_csv:
                text_id       = row[0];
                text_filename = row[1];
                text_path     = texts_directory+"/"+text_filename;

                print("Generating tokenized version of "+text_path);

                text_file = open(text_path);

                stoks = smooth_tok.tokenize(text_file.read());
                text_file.seek(0);
                rtoks = raw_tok.tokenize(text_file.read());

                raw_file = open(text_path+".raw", "w+");

                raw_file.write(" ".join(rtoks));

                raw_file.close();

                text_file.close();

                for n in n_vector:
                        print("Generating "+str(n)+"-grams for "+text_path);

                        ################################################# 
                        # Compute frequencies for raw grams
                        ################################################# 
                        rgrams      = nltk.ngrams(rtoks, n)
                        rgrams_freq = {};

                        for gram_vector in rgrams:
                                gram = " ".join(gram_vector);

                                if gram in rgrams_freq:
                                        rgrams_freq[gram] += 1;
                                else:
                                        rgrams_freq[gram] = 1;

                        ################################################# 
                        # Store raw gram frequencies as CSV 
                        ################################################# 
                        for item in rgrams_freq.items():

                                gram = item[0];
                                freq = str(item[1]);

                                rgrams_csv.write(str(gram_id)+","+str(text_id)+","+str(freq)+","+str(n)+","+gram+"\n");

                                gram_id += 1;

                        ################################################# 
                        # Compute frequencies for smoothed grams
                        ################################################# 
                        sgrams      = nltk.ngrams(stoks, n)
                        sgrams_freq = {};

                        for gram_vector in sgrams:
                                gram = " ".join(gram_vector);

                                if gram in sgrams_freq:
                                        sgrams_freq[gram] += 1;
                                else:
                                        sgrams_freq[gram] = 1;
                    
                        ################################################# 
                        # Store smooth gram frequencies as CSV 
                        ################################################# 
                        for item in sgrams_freq.items():

                                gram = item[0];
                                freq = str(item[1]);

                                sgrams_csv.write(str(gram_id)+","+str(text_id)+","+str(freq)+","+str(n)+","+gram+"\n");

                                gram_id += 1;


        rgrams_csv.close();
        sgrams_csv.close();
		



def main(argv):
        text_directory = "";
        meta_file = "";
        rgram_file = "";
        sgram_file = "";
        database ="";

        try:
                opts, args = getopt.getopt(argv,"c:m:s:",["make-database", "make-gramfile", "text-directory=", "metafile=", "rgramfile=", "sgramfile=", "database="])

        except getopt.GetoptError:
                print "USAGE:\n\twig.py -c <corpus_directory> -m <metadata_csv>"
                sys.exit(2)

        if len(opts) == 0:
                print "USAGE:\n\twig.py -c <corpus_directory> -m <metadata_csv>"
                sys.exit(2)
   
        for opt, arg in opts:
                if opt in ("--text-directory"):
                        text_directory = arg
                if opt in ("--metafile"):
                        meta_file = arg
                if opt in ("--rgramfile"):
                        rgram_file = arg;
                if opt in ("--sgramfile"):
                        sgram_file = arg;
                if opt in ("--database"):
                        database = arg;

        if database is not "":
                create_sqlite_database(meta_file, rgram_file, sgram_file, database);
        else:
                generate_grams(text_directory, meta_file, [1,2,3,4,5]);

if __name__ == "__main__":
        main(sys.argv[1:])
