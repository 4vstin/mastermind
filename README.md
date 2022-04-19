# Mastermind
Mastermind is a strategy board game created in 1970 by the company Pressman, I recreated this game in Python for fun.
(Source code not availiable for version 1.2.3 (because I am lazy and it is basically the same thing as 1.2))

## How to play
1. Download and Install the Python coding language at https://www.python.org/. (Optional)
2. Download the [mastermind installer 1.3 beta 1.8.exe](https://github.com/4vstin/mastermind/raw/main/mastermind%20installer%201.3%20beta%201.8.exe) file.
You may have to allow the file through your antivirus software.
3. Locate the file that the installer downloaded.
4. Run the mastermind.exe file.

## Game instructions
The goal of the game is to match the hidden 4 digit code in 10 attempts or less.
You start off with no information, you can select a color on the left and click on the empty slots on the bottom to fill them in.
Once you've filled all 4 slots press the guess button. The game will then give you some different colored pegs.
There are 2 types of pegs, white ones and black ones. If you get a black peg it means that one of the colors you just guessed is correct, but you most likely don't know which one.
White ones mean that the color you guessed is in the code but not in the right location.
You can only recieve a max of four pegs each guess, if you don't receive four pegs it means that the amount of pegs you are missing are indicating that that amount of colors are not in the code. Here is an example.

![image](https://user-images.githubusercontent.com/86859941/146692765-d41cc413-68c7-4098-9004-7ae262946dff.png)

This means that one color is correct, one color is located in the code but is in the wrong location, and that two of the colors are not in the code at all.
You do not know which colors these pegs are pointing at though.
You can use this information to slowly narrow down the guesses until eventually you will crack the code. It usually takes around 8 guesses for people to crack it and learning the strategy may be confusing at first.
