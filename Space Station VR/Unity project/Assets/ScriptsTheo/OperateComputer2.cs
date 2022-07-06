using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using Valve.VR.InteractionSystem;

public class OperateComputer2 : MonoBehaviour
{
    [SerializeField]
    private GameObject DartsBoard;
    [SerializeField]
    private Text dartNumbersReady;
    [SerializeField]
    private GameObject DartsPoint1;
    [SerializeField]
    private GameObject DartsPoint2;
    [SerializeField]
    private GameObject DartsPoint3;
    [SerializeField]
    private GameObject key;
    [SerializeField]
    private GameObject card;
    [SerializeField]
    private Text screenText;
    [SerializeField]
    private CanvasGroup screenCG;
    [SerializeField]
    private Color startingColor;
    [SerializeField]
    private GameObject leftHand;
    [SerializeField]
    private GameObject rightHand;
    [SerializeField]
    private GameObject UFOParent;
    [SerializeField]
    private List<OperateSwitchButton> switchButtons;
    [SerializeField]
    private AudioSource startSound;
    [SerializeField]
    private GameObject DistanceChild;
    [SerializeField]
    private GameObject PlayerFollowHead;
    [SerializeField]
    private GameObject DistanceLine;


    private InteractableFunctionality interFunc;
    private AudioSource audioS;
    private OpenMetalBoxScene2 openMetalBox;
    private DartsGame dartsGame;

    private bool started = false;

    private bool ruleWritten = false;
    //private int darts = 0;
    private float defaultDistance = 0f;

    
    // Start is called before the first frame update
    void Start()
    {
        interFunc = FindObjectOfType<InteractableFunctionality>();
        audioS = GetComponent<AudioSource>();
        openMetalBox = FindObjectOfType<OpenMetalBoxScene2>();
        defaultDistance = Vector3.Distance(DistanceChild.transform.position, this.transform.position);
    }

    // Update is called once per frame
    void Update()
    {
        if (started)
        {
            bool correctDist = Vector3.Distance(this.transform.position, PlayerFollowHead.transform.position) > defaultDistance;
            if (!correctDist && !ruleWritten)
            {
                screenText.text = "Please keep\nthe distance!";
                DartsBoard.SetActive(false);
                dartNumbersReady.gameObject.SetActive(false);
                ruleWritten = true;
            }
            else if(correctDist && ruleWritten)
            {
                screenText.text = "";
                DartsBoard.SetActive(true);
                dartNumbersReady.gameObject.SetActive(true);
                ruleWritten = false;
            }
            if(dartsGame.darts == 3)
            {
                //game ready
                StartCoroutine(gameEnded());
                dartsGame.darts++;
            }
        }
        else
        {
            if (switchButtons[0].isUp == true && switchButtons[1].isUp == false && switchButtons[2].isUp == false && switchButtons[3].isUp == true)
            {
                started = true;
                if (!DartsBoard.activeInHierarchy)
                {
                    startSound.Play();
                    DartsBoard.SetActive(true);
                    dartNumbersReady.gameObject.SetActive(true);
                    DistanceLine.SetActive(true);
                    dartsGame = FindObjectOfType<DartsGame>();
                }
            }
        }
    }

    private IEnumerator gameEnded()
    {
        yield return new WaitForSeconds(1);
        //play some sound
        DartsBoard.SetActive(false);
        dartNumbersReady.gameObject.SetActive(false);
        screenCG.alpha = 1;
        screenText.text = "Game ended!";
        while (screenCG.alpha < 1)
        {
            screenCG.alpha += 0.01f;
            yield return new WaitForEndOfFrame();
        }
        StartCoroutine(openMetalBox.takeLockDown());
        UFOParent.SetActive(true);


        yield return new WaitForSeconds(10);
        Destroy(DartsPoint1);
        Destroy(DartsPoint2);
        Destroy(DartsPoint3);

        Destroy(this);
    }
}
