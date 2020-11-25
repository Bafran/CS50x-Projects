// Implements a dictionary's functionality

#include <stdbool.h>
#include "dictionary.h"
#include <strings.h>
#include <string.h>
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node;

int wordcount = 0;

// Number of buckets in hash table
//From Algorithms Illustrator on youtube
const unsigned int N = (LENGTH + 1) * 'z';

// Hash table
node *table[N];

// Returns true if word is in dictionary else false
bool check(const char *word)
{
    int index = hash(word);
    node *cursor = table[index];
    
    while(cursor != NULL)
    {
        if(strcasecmp(cursor->word ,word) == 0)
        {
         return true;
        }
        cursor = cursor->next;
    }
    
    return false;
}

// Hashes word to a number
//From Algorithms Illustrator on youtube
unsigned int hash(const char *word)
{
    // TODO
    int sum = 0;
    for (int i = 0; i < strlen(word); i++)
    {
        sum += tolower(word[i]);
    }
    return (sum % N);
}

// Loads dictionary into memory, returning true if successful else false
bool load(const char *dictionary)
{
    // TODO
    //File input from pset4
    FILE *input = fopen(dictionary, "r");
    if (input == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", dictionary);
        return false;
    }
    
    //Read
    char word[LENGTH];
    while (fscanf(input, "%s", word) != EOF)
    {
        node *node1 = malloc(sizeof(node));
        
        if (node1 == NULL)
        {
            return false;
        }
        
        strcpy(node1->word, word);
        
        node1->next = NULL;
        
        int index = hash(word);
        
        if(table[index] == NULL)
        {
            node1->next = NULL;
            table[index] = node1;
        }
        else
        {
            node1->next = table[index];
            table[index] = node1;
            
        }
        wordcount++;
    }
    fclose(input);
    return true;
}

// Returns number of words in dictionary if loaded else 0 if not yet loaded
unsigned int size(void)
{
    return wordcount;
}

// Unloads dictionary from memory, returning true if successful else false
bool unload(void)
{
    for(int i = 0; i < N; i++)
    {
        node *cursor = table[i];
        
        while(cursor != NULL)
        {
            node *tmp = cursor;
            cursor = cursor->next;
            free(tmp);
        }
    }
    return true;
}
