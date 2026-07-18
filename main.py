import random
import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import time

# Initialize camera
cap = cv2.VideoCapture(0)
cap.set(3, 640) # sets the width of the video frame to 640 pixels
cap.set(4, 480) # sets the height of the video frame to 480 pixels
detector = HandDetector(maxHands=1)

# Variables to track game state
timer = 0
stateResult = False
startGame = False
scores = [0, 0]  # [AI, Player]
round_number = 0
max_rounds = 5  # Number of rounds per session
game_over = False
initialTime = 0  # Track time for the current round
showAIMove = False  # To control display of AI move
showResultTime = 0  # Time to show the AI move
result_display_time = 2  # Set to 2 seconds for result image display
result_displayed = False  # Flag to check if result is displayed
result_display_time_start = 0  # Start time for result display
imgResult = None  # Variable to hold the result image

# Function to display the session result
def display_session_result():
    global imgBG, result_displayed, imgResult
    if scores[1] > scores[0]:
        #cv2.putText(imgBG,'Congratulations!!! You won. I\'ll beat you next time', (505, 180), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 4)
        imgResult = cv2.imread('A\Resources\PlayerWins.png')  # Load player win image
        time.sleep(2)
        cv2.waitKey(2000)
    elif scores[0] > scores[1]:
        #cv2.putText(imgBG,'Hehe, AI won. Wanna lose again?', (505, 180), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 4)
        imgResult = cv2.imread('A\Resources\Aiwins.png')  # Load AI win image
        time.sleep(2)
        cv2.waitKey(2000)
    else:
        #cv2.putText(imgBG,'It\'s a tie. You dare win?', (505, 180), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 4)
        imgResult = cv2.imread('A\Resources\Tie.png')  # Load draw image
        time.sleep(2)
        cv2.waitKey(2000)
    if imgResult is not None:  # Check if the image loaded successfully
        imgResult = cv2.resize(imgResult, (800, 450))  # Resize to fit on screen
        imgBG[150:600, 200:1000] = imgResult  # Overlay result image
        result_displayed = True  # Set flag to indicate result is displayed

# Function to reset for a new session
def reset_game():
    global startGame, round_number, scores, game_over, showAIMove, stateResult, result_displayed
    startGame = True
    round_number = 0
    scores = [0, 0]  # Reset scores for a new session
    game_over = False  # Reset game state
    showAIMove = False  # Reset AI move display flag
    stateResult = False  # Reset round result flag
    result_displayed = False  # Reset result display flag
    imgResult = None
    print("New session started.")

# Main game loop
while True:
    imgBG = cv2.imread("A\Resources\BG.png")  # Background image
    success, img = cap.read()

    imgScaled = cv2.resize(img, (0, 0), None, 0.875, 0.875)
    imgScaled = imgScaled[:, 80:480]

    # Find Hands
    hands, img = detector.findHands(imgScaled)  # With draw

    if startGame and not game_over:
        if stateResult is False:  # During the game (before result is shown)
            timer = time.time() - initialTime
            cv2.putText(imgBG, str(int(timer)), (605, 435), cv2.FONT_HERSHEY_PLAIN, 6, (255, 0, 255), 4)

            if timer > 3:  # After 3 seconds, determine the result
                stateResult = True
                timer = 0

                if hands:
                    playerMove = None
                    hand = hands[0]
                    fingers = detector.fingersUp(hand)
                    if fingers == [0, 0, 0, 0, 0]:
                        playerMove = 1  # Rock
                    if fingers == [1, 1, 1, 1, 1]:
                        playerMove = 2  # Paper
                    if fingers == [0, 1, 1, 0, 0]:
                        playerMove = 3  # Scissors

                    randomNumber = random.randint(1, 3)
                    imgAI = cv2.imread(f'A\Resources\{randomNumber}.png', cv2.IMREAD_UNCHANGED)
                    imgBG = cvzone.overlayPNG(imgBG, imgAI, (149, 310))
                    showAIMove = True  # Enable AI move display
                    showResultTime = time.time()  # Set time to show AI move

                    # Player Wins
                    if (playerMove == 1 and randomNumber == 3) or \
                            (playerMove == 2 and randomNumber == 1) or \
                            (playerMove == 3 and randomNumber == 2):
                        scores[1] += 1

                    # AI Wins
                    if (playerMove == 3 and randomNumber == 1) or \
                            (playerMove == 1 and randomNumber == 2) or \
                            (playerMove == 2 and randomNumber == 3):
                        scores[0] += 1

                round_number += 1

    # Show AI move for 2 seconds
    if showAIMove and time.time() - showResultTime < 2:
        imgBG = cvzone.overlayPNG(imgBG, imgAI, (149, 310))
    elif showAIMove and time.time() - showResultTime >= 2:
        showAIMove = False  # Disable AI move display
        if round_number >= max_rounds:  # After all rounds, show session result
            game_over = True
            display_session_result()  # Display result at the end of session
            result_display_time_start = time.time()  # Start result display time
        else:
            initialTime = time.time()  # Reset timer for the next round
            stateResult = False  # Ready for the next round

    imgBG[234:654, 795:1195] = imgScaled

    # Display the current score
    cv2.putText(imgBG, str(scores[0]), (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
    cv2.putText(imgBG, str(scores[1]), (1112, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)

    # Display current round number
    #cv2.putText(imgBG, f'Round: {round_number}/{max_rounds}', (505, 180), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 4)

    # Show the result image for a few seconds after the game session
    if game_over and result_displayed:
        # Calculate elapsed time since the result was displayed
        elapsed_time = time.time() - result_display_time_start
        if elapsed_time < 2:  # Check if less than 2 seconds have passed
            # Keep showing the result image for the specified duration
            pass
        else:
            result_displayed = False  # Reset result display flag
            # Prompt user to restart or quit
            #cv2.putText(imgBG, "Press 'r' to Restart or 'q' to Quit", (350, 450), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)
            #cv2.waitKey(1)
        '''if time.time() - result_display_time_start < result_display_time:
            # Keep showing the result image for 2 seconds
            # Keep showing the result image for 2 seconds
            if imgResult is not None:  # Check if result image is valid
                imgBG[150:600, 200:1000] = imgResult  # Overlay the result image
        else:
            game_over = False  # Reset game_over to allow for restart
            cv2.putText(imgBG, "Press 'r' to Restart or 'q' to Quit", (350, 450), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)
'''
    # Show the background image
    cv2.imshow("BG", imgBG)

    # Key press logic
    key = cv2.waitKey(1)
    if key == ord('s') and not startGame:  # Start new session
        reset_game()
        initialTime = time.time()  # Start timer for the first round
    elif key == ord('r') and game_over:  # Restart after session ends
        reset_game()
        initialTime = time.time()  # Start timer for the first round
    elif key == ord('q'):  # Quit the game
        break

# Release camera and close windows
cap.release()
cv2.destroyAllWindows()