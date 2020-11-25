#include "helpers.h"
#include <math.h>
#include <stdio.h>

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int av =  round((image[i][j].rgbtBlue + image[i][j].rgbtRed + image[i][j].rgbtGreen) / 3.0);
            image[i][j].rgbtBlue = av;
            image[i][j].rgbtGreen = av;
            image[i][j].rgbtRed = av;
        }
    }
    return;
}

int overflow (RGB)
{
    if (RGB > 255)
    {
        return 255;
    }
    else if (RGB < 0)
    {
        return 0;
    }
    else
    {
        return RGB;
    }
}
// Convert image to sepia
void sepia(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int originalRed = image[i][j].rgbtRed;
            int originalBlue = image[i][j].rgbtBlue;
            int originalGreen = image[i][j].rgbtGreen;
            
            int sepiaRed = overflow(round(.393 * originalRed + .769 * originalGreen + .189 * originalBlue));
            int sepiaGreen = overflow(round(.349 * originalRed + .686 * originalGreen + .168 * originalBlue));
            int sepiaBlue = overflow(round(.272 * originalRed + .534 * originalGreen + .131 * originalBlue));
            
            image[i][j].rgbtRed = sepiaRed;
            image[i][j].rgbtGreen = sepiaGreen;
            image[i][j].rgbtBlue = sepiaBlue;
        }
    }
    return;
}

// Reflect image horizontally
void swap(RGBTRIPLE *first, RGBTRIPLE *second)
{
    RGBTRIPLE tmp = *first;
    *first = *second;
    *second = tmp;
}

void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width / 2; j++)
        {
            swap(&image[i][j], &image[i][width - j - 1]);
        }
    }
    return;
}

// Blur image
RGBTRIPLE blurpix(int i, int j, int height, int width, RGBTRIPLE image[height][width])
{
    int new_Red = 0;
    int new_Green = 0;
    int new_Blue = 0;
    
    int pixelsav = 0;
    
    RGBTRIPLE pixel;
    
    for (int dx = -1; dx <= 1; dx++)
    {
        for (int dy = -1; dy <= 1; dy++)
        {
            if(i + dx < height && j + dy < width && i + dx >= 0 && j + dy>= 0)
            {
                new_Red += image[i + dx][j + dy].rgbtRed;
                new_Green += image[i + dx][j + dy].rgbtGreen;
                new_Blue += image[i + dx][j + dy].rgbtBlue;
                
                pixelsav++;
            }
        }
    }
    
    pixel.rgbtRed = overflow((int)((float)(new_Red - image[i][j].rgbtRed) / (pixelsav - 1)));
    pixel.rgbtGreen = overflow((int)((float)(new_Green - image[i][j].rgbtGreen) / (pixelsav - 1)));
    pixel.rgbtBlue = overflow((int)((float)(new_Blue - image[i][j].rgbtBlue) / (pixelsav - 1)));
    
    //printf("%i\n", pixelsav);
    return pixel;
}

void blur(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE new_image[height][width];
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            new_image[i][j] = blurpix(i, j, height, width, image);
        }
    }
    
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            image[i][j] = new_image[i][j];
        }
    }
    return;
}
