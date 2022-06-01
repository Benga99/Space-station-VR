using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using Valve.VR.InteractionSystem;
using Valve.VR;

public class OperateComputerScene4 : MonoBehaviour
{
    [SerializeField]
    private GameObject half_key;
    [SerializeField]
    private GameObject metal_box_key;
    [SerializeField]
    private GameObject card;
    [SerializeField]
    private Text screenText;
    [SerializeField]
    private Material screenMat;
    [SerializeField]
    private Color startingColor;
    [SerializeField]
    private Color mainColor;
    [SerializeField]
    private GameObject leftHand;
    [SerializeField]
    private GameObject rightHand;
    [SerializeField]
    private SteamVR_Action_Boolean grabPinch;
    [SerializeField]
    private SteamVR_Input_Sources inputSource = SteamVR_Input_Sources.Any;


    private InteractableFunctionality interFunc;
    private WarningDisplay warDisplay;

    private bool fired = false;
    private bool keyIntroduced = false;
    private bool triggerPressed = false;

    private int gameInteration = 0;
    private float totalScore = 0;
    // Start is called before the first frame update
    void Start()
    {
        interFunc = FindObjectOfType<InteractableFunctionality>();
        warDisplay = GetComponent<WarningDisplay>();
        screenMat.color = startingColor;
        grabPinch.AddOnChangeListener(OnTriggerPressed, inputSource);

    }

    // Update is called once per frame
    void Update()
    {

    }

    private void OnCollisionEnter(Collision other)
    {

    }

    private void OnTriggerEnter(Collider other)
    {
        if (!keyIntroduced)
        {
            if (other.gameObject.tag == "PCCard" && (rightHand.GetComponent<Hand>().currentAttachedObject == card ||
                                                    leftHand.GetComponent<Hand>().currentAttachedObject == card))
            {
                GameObject hand = GetTheHand(other.gameObject);

                hand.GetComponent<Hand>().DetachObject(card);

                card.SetActive(false);
                keyIntroduced = true;
                StartCoroutine(startGame());

            }
        }
    }



    private GameObject GetTheHand(GameObject card)
    {
        if (Vector3.Distance(card.transform.position, leftHand.transform.position) < Vector3.Distance(card.transform.position, rightHand.transform.position))
        {
            return leftHand;
        }
        else
        {
            return rightHand;
        }
    }

    private IEnumerator startGame()
    {
        warDisplay.killThis();

        half_key.SetActive(false);

        float index = 0;
        while (index < 1)
        {
            screenText.GetComponent<CanvasGroup>().alpha -= 0.01f;

            screenMat.color = Color.Lerp(startingColor, mainColor, index);

            index += 0.01f;
            yield return new WaitForEndOfFrame();
        }

        screenText.fontSize = 35;
        screenText.color = Color.white;
        screenText.text = "Press GRAB on any\nhand when the screen\n gets green as fast\n as you can!\n\nPress GRAB to continue";
        screenText.GetComponent<CanvasGroup>().alpha = 1;

        triggerPressed = false;
        while (!triggerPressed)
        {
            yield return new WaitForEndOfFrame();
        }
        screenText.text = "The goal is to\n have a reaction\n time smaller than 0.5\nseconds on each turn!\n\nPress GRAB to continue";
        yield return new WaitForSeconds(3);
        triggerPressed = false;
        while (!triggerPressed)
        {
            yield return new WaitForEndOfFrame();
        }

        screenText.fontSize = 80;
        hapticFeel("3", 0.3f, 5);
        yield return new WaitForSeconds(1);
        hapticFeel("2", 0.3f, 5);
        yield return new WaitForSeconds(1);
        hapticFeel("1", 0.3f, 5);
        yield return new WaitForSeconds(1);
        hapticFeel("GO!", 1f, 10);

        StartCoroutine(redGreen());

        
    }

    private IEnumerator redGreen()
    {
        gameInteration++;
        if(gameInteration < 4)
        {
            screenMat.color = Color.red;
            
            float timer = 0;

            while (screenText.GetComponent<CanvasGroup>().alpha > 0)
            {
                screenText.GetComponent<CanvasGroup>().alpha -= 0.02f;
                yield return new WaitForEndOfFrame();
            }
            screenText.fontSize = 50;

            yield return new WaitForSeconds(Random.Range(2, 5));
            screenMat.color = Color.green;
            triggerPressed = false;
            while (!triggerPressed)
            {
                timer += Time.deltaTime;
                yield return new WaitForEndOfFrame();
            }

            screenText.GetComponent<CanvasGroup>().alpha = 1;
            screenText.text = timer.ToString("0.000") + " seconds!";
            totalScore += timer;

            yield return new WaitForSeconds(5);

            StartCoroutine(redGreen());
        }
        else
        {
            screenText.fontSize = 40;
            if (totalScore < 1.5f)
            {
                
                screenText.GetComponent<CanvasGroup>().alpha = 0;
                screenText.text = $"You won!\nYou earned the key!\nScore: {totalScore.ToString("0.000")}s\n\nPress GRAB\nto continue!";
                while (screenText.GetComponent<CanvasGroup>().alpha < 1)
                {
                    screenText.GetComponent<CanvasGroup>().alpha += 0.02f;
                    yield return new WaitForEndOfFrame();
                }

                StartCoroutine(pushKey());

                while (!triggerPressed)
                {
                    yield return new WaitForEndOfFrame();
                }

                metal_box_key.SetActive(true);
            }
            else
            {
                triggerPressed = false;
                gameInteration = 0;
                
                screenText.GetComponent<CanvasGroup>().alpha = 0;
                screenText.text = $"You lost!\nPlay again!\nScore: {totalScore.ToString("0.000")}s\n\nPress GRAB \nto play again";
                while (screenText.GetComponent<CanvasGroup>().alpha < 1)
                {
                    screenText.GetComponent<CanvasGroup>().alpha += 0.02f;
                    yield return new WaitForEndOfFrame();
                }

                while (!triggerPressed)
                {
                    yield return new WaitForEndOfFrame();
                }

                totalScore = 0;
                StartCoroutine(redGreen());
            }
        }
        
        
    }

    private IEnumerator pushKey()
    {
        float distance = 0;
        while(distance < 0.2f)
        {
            metal_box_key.transform.position = new Vector3(metal_box_key.transform.position.x,
                                                      metal_box_key.transform.position.y,
                                                      metal_box_key.transform.position.z - 0.001f);
            distance += 0.001f;
            yield return new WaitForEndOfFrame();
        }
    }

    private void OnTriggerPressed(SteamVR_Action_Boolean fromAction, SteamVR_Input_Sources fromSource, bool newState)
    {
        triggerPressed = true;
    }

    private void hapticFeel(string text, float duration, float strength)
    {
        screenText.text = text;
        SteamVR_Actions.default_Haptic[SteamVR_Input_Sources.LeftHand].Execute(0, duration, strength, 1);
        SteamVR_Actions.default_Haptic[SteamVR_Input_Sources.RightHand].Execute(0, duration, strength, 1);
    }


}
