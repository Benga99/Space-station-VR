using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using Valve.VR.InteractionSystem;

public class OperateComputer2 : MonoBehaviour
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
    private AudioSource audioS;

    private bool started = false;

    private bool fired = false;
    private bool keyIntroduced = false;
    // Start is called before the first frame update
    void Start()
    {
        interFunc = FindObjectOfType<InteractableFunctionality>();
        audioS = GetComponent<AudioSource>();
        screenMat.color = startingColor;
    }

    // Update is called once per frame
    void Update()
    {
        if (started)
        {
            started = false;
            StartCoroutine(initializeScreen());
        }
    }

    private void OnTriggerEnter(Collider other)
    {
        //this works 
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

                this.gameObject.GetComponent<MeshCollider>().isTrigger = false;
                
            }
        }
        else
        {
            if (other.gameObject.tag == "Fire" && !fired)
            {
                interFunc.DeactivateRigidbodyConstraints(key);
                key.GetComponent<Rigidbody>().AddForce(-5f, 0, 0);
                Debug.Log("Force added 1");
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

    private IEnumerator initializeScreen()
    {
        Color baseColor = screenMat.color;
        Color white = Color.white;
        yield return new WaitForEndOfFrame();

    }

}
