using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using Valve.VR.InteractionSystem;

public class OperateComputerScene4 : MonoBehaviour
{
    [SerializeField]
    private GameObject half_key;
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


    private InteractableFunctionality interFunc;

    private bool fired = false;
    private bool keyIntroduced = false;
    // Start is called before the first frame update
    void Start()
    {
        interFunc = FindObjectOfType<InteractableFunctionality>();
        screenMat.color = startingColor;
    }

    // Update is called once per frame
    void Update()
    {

    }

    private void OnTriggerEnter(Collider other)
    {
        //this works 
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
        else
        {
            if (other.gameObject.tag == "Fire" && !fired)
            {
                //interFunc.DeactivateRigidbodyConstraints(half_key);
                //Do something with the key, move it to the user
                //half_key.GetComponent<Rigidbody>().AddForce(-5f, 0, 0);
                fired = true;
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
        float index = 0;
        while (screenText.GetComponent<CanvasGroup>().alpha > 0 || index < 1)
        {
            screenText.GetComponent<CanvasGroup>().alpha -= 0.02f;

            screenMat.color = Color.Lerp(startingColor, mainColor, index);

            index += 0.02f;

            yield return new WaitForEndOfFrame();
        }

        screenText.text = "Press SELECT on either hand when the screen gets green as fast as you can!";
        yield return new WaitForSeconds(5);
        screenText.text = "3";
        yield return new WaitForSeconds(0.5f);
        screenText.text = "2";
        yield return new WaitForSeconds(0.5f);
        screenText.text = "1";
        yield return new WaitForSeconds(0.5f);

        screenMat.color = Color.red;

        screenText.text = "GO!";
        while (screenText.GetComponent<CanvasGroup>().alpha > 0)
        {
            screenText.GetComponent<CanvasGroup>().alpha -= 0.02f;
            yield return new WaitForEndOfFrame();
        }
        yield return new WaitForSeconds(Random.Range(2, 5));
        screenMat.color = Color.green;

    }
}
