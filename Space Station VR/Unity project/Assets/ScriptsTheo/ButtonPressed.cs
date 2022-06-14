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
    private GameObject canvas;

    
    public bool pressed = false;

    private void OnTriggerEnter(Collider other)
    {
        if ((other.gameObject.transform.parent.gameObject.transform.parent.gameObject.name == "HandColliderRight(Clone)" ||
            other.gameObject.transform.parent.gameObject.transform.parent.gameObject.name == "HandColliderLeft(Clone)") && !pressed)
        {
            pressed = true;
            Debug.Log("button pressed trig");
            StartCoroutine(PressButton());
        }
    }

    private IEnumerator PressButton()
    {
        while(press.transform.localPosition.z > -0.078f)
        {
            press.transform.localPosition = new Vector3(press.transform.localPosition.x, press.transform.localPosition.y, press.transform.localPosition.z - Time.deltaTime / 3f);
            yield return new WaitForEndOfFrame();
            yield return new WaitForEndOfFrame();
        }
        canvas.SetActive(true);
    }
}
