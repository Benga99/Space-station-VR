using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Valve.VR;
using Valve.VR.InteractionSystem;

public class BreakBottle : MonoBehaviour
{
    [SerializeField]
    private GameObject breakableBottle;
    [SerializeField]
    private GameObject messagePlane;
    [SerializeField]
    private AudioSource breakAudio;

    private InteractableFunctionality interFunc;
    private RiddleManager1 riddleManager;
    private SwitchBox switchBox;

    private void Start()
    {
        interFunc = FindObjectOfType<InteractableFunctionality>();
        switchBox = FindObjectOfType<SwitchBox>();
    }

    private void OnCollisionEnter(Collision collision)
    {
        //if it is not the player
        if(collision.gameObject.name == "Floorready")
        {
            breakAudio.Play();
            breakableBottle.transform.position = this.gameObject.transform.position;
            breakableBottle.transform.rotation = this.gameObject.transform.rotation;
            breakableBottle.SetActive(true);
            messagePlane.transform.position = this.gameObject.transform.position + new Vector3(0.1f, 0.1f, 0.1f);
            messagePlane.transform.rotation = this.gameObject.transform.rotation;
            messagePlane.SetActive(true);

            switchBox.SetActiveDoorInteractable();
            interFunc.riddlesBool[1] = true;
            
            Destroy(this.gameObject);
        }
    }

    
}
