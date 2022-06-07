using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using Valve.VR;
using Valve.VR.InteractionSystem;

public class OperateComputerScene3 : MonoBehaviour
{
    [SerializeField]
    private GameObject fireExt;
    [SerializeField]
    private GameObject USBStick;
    [SerializeField]
    private Material screenMat;
    [SerializeField]
    private Material startingMat;
    [SerializeField]
    private Material pizzaMat;
    [SerializeField]
    private Text screenText;
    [SerializeField]
    private GameObject leftHand;
    [SerializeField]
    private GameObject rightHand;
    [SerializeField]
    private Color startingColor;

    private InteractableFunctionality interFunc;

    private bool keyIntroduced = false;

    // Start is called before the first frame update
    void Start()
    {
        interFunc = FindObjectOfType<InteractableFunctionality>();
        screenMat.color = startingColor;
        fireExt.GetComponent<MeshRenderer>().material = startingMat;

    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void OnTriggerEnter(Collider other)
    {
        if (!keyIntroduced)
        {
            if (other.gameObject.tag == "USB" && (rightHand.GetComponent<Hand>().currentAttachedObject == USBStick ||
                                                    leftHand.GetComponent<Hand>().currentAttachedObject == USBStick))
            {
                GameObject hand = GetTheHand(other.gameObject);

                hand.GetComponent<Hand>().DetachObject(USBStick);

                USBStick.SetActive(false);
                keyIntroduced = true;
                screenText.fontSize = 40;
                screenText.text = "Put the fire\nextinguisher\nback in place!";
                screenMat.color = Color.red;
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
}
