using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Valve.VR;
using UnityEngine.UI;

public class StartMessage : MonoBehaviour
{
    public Canvas EndMessageCanvas;
    public CanvasGroup EndMessageCG;
    public Canvas MessageCanvas;
    public AudioSource audioK;
    public string message;
    public CanvasGroup messageCG;

    public SteamVR_Action_Boolean grabPinch; //Grab Pinch is the trigger, select from inspecter
    public SteamVR_Input_Sources inputSource = SteamVR_Input_Sources.Any;//which controller
                                                                         // Use this for initialization


    private void Start()
    {
        //message = "Hello Captain! You just woke up and realized your crew left you behind. The aliens will take over the ship shortly and you are the only one left on the ship. Find your way out! Press SELECT to continue!";
        MessageCanvas.GetComponent<Text>().text = "";
        char[] m = message.ToCharArray();
        StartCoroutine(writeMessage(m));

        //MessageCanvas.GetComponent<Text>().text = $"Hello Captain! You just woke up and realized your crew left you behind. The aliens will take over the ship shortly and you are the only one left on the ship. Find your way out! Press SELECT to continue!";
    }

    private void Update()
    {
        
    }

    private IEnumerator writeMessage(char[] m)
    {
        yield return new WaitForSeconds(1f);
        float j = 0;
        while (j < 1)
        {
            messageCG.alpha = j;
            j += 0.01f;
            yield return new WaitForEndOfFrame();
        }
        //yield return new WaitForSeconds(1f);
        audioK.Play();
        yield return new WaitForSeconds(0.5f);
        string mes = "";
        
        for(int i = 0; i < m.Length; i++)
        {
            //mes = string.Concat(mes, m[i]);
            mes = mes + m[i];
            MessageCanvas.GetComponent<Text>().text = mes;
            yield return new WaitForSeconds(0.06f);
        }
        audioK.Stop();
        if (grabPinch != null)
        {
            grabPinch.AddOnChangeListener(OnTriggerPressedOrReleased, inputSource);
        }
    }

    private IEnumerator writeMessageEnd(char[] m)
    {
        yield return new WaitForSeconds(1f);
        float j = 0;
        while (j < 1)
        {
            EndMessageCG.alpha = j;
            j += 0.01f;
            yield return new WaitForEndOfFrame();
        }
        //yield return new WaitForSeconds(1f);
        audioK.Play();
        yield return new WaitForSeconds(0.5f);
        string mes = "";

        for (int i = 0; i < m.Length; i++)
        {
            //mes = string.Concat(mes, m[i]);
            mes = mes + m[i];
            EndMessageCanvas.GetComponent<Text>().text = mes;
            yield return new WaitForSeconds(0.06f);
        }
        audioK.Stop();
    }


    private void OnDisable()
    {
        if (grabPinch != null)
        {
            grabPinch.RemoveOnChangeListener(OnTriggerPressedOrReleased, inputSource);
        }
    }

    private void OnTriggerPressedOrReleased(SteamVR_Action_Boolean fromAction, SteamVR_Input_Sources fromSource, bool newState)
    {
        audioK.Stop();
        //Destroy(MessageCanvas.gameObject);
        //Destroy(this);
        messageCG.alpha = 0;
        MessageCanvas.gameObject.SetActive(false);
    }

    public void onFinishEscapeRoom()
    {
        EndMessageCanvas.gameObject.SetActive(true);
        //EndMessageCG.alpha = 1;
        EndMessageCanvas.GetComponent<Text>().fontSize = 100;
        StartCoroutine(writeMessageEnd("You won!! - You can take off your headset now".ToCharArray()));
    }
}