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


    private InteractableFunctionality interFunc;
    private AudioSource audioS;
    private OpenMetalBoxScene2 openMetalBox;

    private bool started = false;

    private bool fired = false;
    private int darts = 0;
    // Start is called before the first frame update
    void Start()
    {
        interFunc = FindObjectOfType<InteractableFunctionality>();
        audioS = GetComponent<AudioSource>();
        openMetalBox = FindObjectOfType<OpenMetalBoxScene2>();
    }

    // Update is called once per frame
    void Update()
    {
        if (started)
        {
            if(darts == 3)
            {
                //game ready
                StartCoroutine(gameEnded());
                //spawn 2 notes -> look in thge fridge
                //TODO 03.06.
            }
        }
    }

    private void OnTriggerEnter(Collider other)
    {
        if(other.gameObject.tag == "Dart" && (rightHand.GetComponent<Hand>().currentAttachedObject == card ||
                                                leftHand.GetComponent<Hand>().currentAttachedObject == card))
        {
            GameObject hand = GetTheHand(other.gameObject);

            hand.GetComponent<Hand>().DetachObject(card);

            card.SetActive(false);
            darts++; 
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

    private IEnumerator gameEnded()
    {
        yield return new WaitForSeconds(1);
        //play some sound
        DartsBoard.SetActive(false);

        screenText.text = "End game!";
        while (screenCG.alpha < 1)
        {
            screenCG.alpha += 0.01f;
            yield return new WaitForEndOfFrame();
        }
        StartCoroutine(openMetalBox.takeLockDown());
    }
}
