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
    // Start is called before the first frame update

    private InteractableFunctionality interFunc;
    private SwitchBox switchBox;

    private void Start()
    {
        interFunc = FindObjectOfType<InteractableFunctionality>();
        switchBox = FindObjectOfType<SwitchBox>();
    }

    private void OnCollisionEnter(Collision collision)
    {
        //if it is not the player
        if(collision.gameObject.name == "Floorready" || collision.gameObject.tag == "Wall")
        {
            
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
