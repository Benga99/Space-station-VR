using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Valve.VR;
using Valve.VR.InteractionSystem;

public class ButtonPressed : MonoBehaviour
{
    [SerializeField]
    private GameObject press;
    [SerializeField]
    private Hand leftHand;
    [SerializeField]
    private Hand rightHand;

    private bool pressed = false;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void OnTriggerEnter(Collider other)
    {
        if((leftHand.hoveringInteractable == press || rightHand.hoveringInteractable == press) && !pressed)
        {
            pressed = true;
            StartCoroutine(PressButton());
        }
    }

    private IEnumerator PressButton()
    {
        while(press.transform.localPosition.z > -0.085f)
        {
            press.transform.localPosition = new Vector3(press.transform.localPosition.x, press.transform.localPosition.y, press.transform.localPosition.z - Time.deltaTime / 2f);
            yield return new WaitForEndOfFrame();
        }
        
    }
}
