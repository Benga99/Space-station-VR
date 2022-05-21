using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using Valve.VR.InteractionSystem;

public class OperateComputer : MonoBehaviour
{
    [SerializeField]
    private GameObject key;
    [SerializeField]
    private GameObject card;
    [SerializeField]
    private Text screenText;
    [SerializeField]
    private Material screenMat;
    [SerializeField]
    private Color startingColor;
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
        StartCoroutine(changeScreen());
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void OnTriggerEnter(Collider other)
    {
        if (!keyIntroduced)
        {
            if(other.gameObject.tag == "PCCard" && (rightHand.GetComponent<Hand>().currentAttachedObject == card ||
                                                    leftHand.GetComponent<Hand>().currentAttachedObject == card))
            {
                GameObject hand = GetTheHand(other.gameObject);

                hand.GetComponent<Hand>().DetachObject(card);

                card.SetActive(false);
                keyIntroduced = true;
                screenText.text = "Hit me with\nsomething\nred! 1";
                screenMat.color = Color.red;
                
            }
        }
        else
        {
            if (other.gameObject.tag == "Fire" && !fired)
            {
                interFunc.DeactivateRigidbodyConstraints(key);
                key.GetComponent<Rigidbody>().AddForce(-1f, 0, 0);
                Debug.Log("Force added");
                fired = true;
            }
        }
    }

    private void OnCollisionEnter(Collision collision)
    {
        //this works    

        if (!keyIntroduced)
        {
            if (collision.gameObject.tag == "PCCard" && (rightHand.GetComponent<Hand>().currentAttachedObject == card || 
                                                          leftHand.GetComponent<Hand>().currentAttachedObject == card))
            {
                GameObject hand = GetTheHand(collision.gameObject);

                hand.GetComponent<Hand>().DetachObject(card);
                card.SetActive(false);

                keyIntroduced = true;
                screenText.text = "Hit me with\nsomething\nred! 2";
                screenMat.color = Color.red;
                

            }
        }
        else
        {
            if (collision.gameObject.tag == "Fire" && !fired)
            {
                interFunc.DeactivateRigidbodyConstraints(key);
                key.GetComponent<Rigidbody>().AddForce(-1f, 0, 0);
                Debug.Log("Force added");
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

    private IEnumerator changeScreen()
    {
        Color baseColor = screenMat.color;
        Color white = Color.white;

        while (keyIntroduced == false)
        {
            screenMat.color = baseColor;
            yield return new WaitForSeconds(0.1f);
            screenMat.color = white;
            yield return new WaitForSeconds(0.05f);
            screenMat.color = baseColor;
            yield return new WaitForSeconds(0.1f);
            screenMat.color = white;
            
            yield return new WaitForSeconds(Random.Range(3, 10));
        }
        StartCoroutine(fadeText());
    }

    private IEnumerator fadeText()
    {
        while(screenText.GetComponent<CanvasGroup>().alpha > 0.07f)
        {
            screenText.GetComponent<CanvasGroup>().alpha -= 0.01f;
            yield return new WaitForSeconds(0.5f);
        }
    }
}
