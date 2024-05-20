# Day :: 11

# Black Jack Game:
import random as r
import art
from rich.console import Console

def elements_sum(lst):
    Sum = 0
    for item in lst:
        Sum += item
    return Sum

def d_choice_with_result(d_choice1, sum_player, bet):
    n = [2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    lst = [d_choice1]
    while True:
        rand = r.choice(n)
        lst.append(rand)
        
        sum_dealer = elements_sum(lst)
        if (sum_dealer >= 17):
            print(f"Dealer Cards: {lst}")
           
            if (sum_dealer > 21 and sum_player <= 21):
               print(f"Win :: ${bet*2}")
                        
            elif (sum_dealer <= 21 and sum_player > 21):
                print(f"Lose :: ${bet*2}")
            
            # Both cases included (i.e. When sum_dealer and sum_player both >= 21 or both <= 21)
            else:
                if (sum_player > sum_dealer):
                    print(f"Win :: ${bet*2}")
                elif (sum_player < sum_dealer):
                    print(f"Lose :: ${bet*2}")
                else:
                    print(f"Push :: ${bet}")

            break

console = Console()
console.clear()
print(art.logo)
       
play = input("Do you want to play a game of Blackjack? (Type 'y' or 'n') -> ")
if (play == 'y'):
    
    player_bet = int(input("Enter the bet amount: $"))
    
    if (player_bet == 0):
        print(f"Bet amount must not be 0.")
        print(" 😊 Run the program again to play the game 😊 ")
    else:
        dealer_bet = player_bet
        print(f"Dealer's Bet = ${dealer_bet}\n")
        
        num = [2, 3, 4, 5, 6, 7, 8, 9, 10]
        player = r.choices(num, k = 2)
        print(f"Your Cards: {player}")
        
        dealer = r.choice(num)
        print(f"Computer's first Card: {dealer}\n")
            
        print("***********************")
        option = """
Type 'h' for Hit
Type 's' for Stand
Type 'd' for Double down
Type 'f' for forefeit
        """
        print(option)
        print("***********************")
        
        press = input("\nType here: ")
        
        console = Console()
        console.clear()
        print(art.logo)

        # for hit:
        if (press == 'h'):
            card_3 = r.choice(num)
            player.append(card_3)
            print(f"Your Cards: {player}")
            p_card_sum = elements_sum(player)
            
            d_choice_with_result(dealer, p_card_sum, player_bet)
        
        # for stand:  
        elif (press == 's'):
            print(f"Your Cards: {player}")
            p_card_sum = elements_sum(player)
            
            d_choice_with_result(dealer, p_card_sum, player_bet)
        
        # for double down: 
        elif (press == 'd'):
            print(f"Your Cards: {player}")
            choose = int(input("Choose a Card from 'Your Cards': "))
            
            if choose not in player:
                print(f"Sorry! {choose} is not in 'Your Cards'")
                print(f"Loss :: ${player_bet*2}")
                
            else:
                player.append(choose)
                print(f"Your Cards: {player}")
                p_card_sum = elements_sum(player)
                
                d_choice_with_result(dealer, p_card_sum, player_bet)
        
        # for forfeit:
        else:
            print(f"Lose :: ${player_bet/2}")  
else:
    print(" 😊 Run the program again to play the game 😊 ")