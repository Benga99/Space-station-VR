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

    private void Start()
    {
        interFunc = FindObjectOfType<InteractableFunctionality>();
    }

    private void OnCollisionEnter(Collision collision)
    {
        //if it is not the player
        if(collision.gameObject.name == "Floorready" || collision.gameObject.name == "Walls2")
        {
            
            breakableBottle.transform.position = this.gameObject.transform.position;
            breakableBottle.transform.rotation = this.gameObject.transform.rotation;
            breakableBottle.SetActive(true);
            messagePlane.transform.position = this.gameObject.transform.position + new Vector3(0.1f, 0.1f, 0.1f);
            messagePlane.transform.rotation = this.gameObject.transform.rotation;
            messagePlane.SetActive(true);
            //GameObject breakable = Instantiate(breakableBottle, this.gameObject.transform.position, this.gameObject.transform.rotation);
            /*
            breakable.transform.GetChild(0).GetComponent<Throwable>()
                .onPickUp.AddListener(() => interFunc.DeactivateRigidbodyConstraints(breakable.transform.GetChild(0).gameObject));
            breakable.transform.GetChild(1).GetComponent<Throwable>()
                .onPickUp.AddListener(() => interFunc.DeactivateRigidbodyConstraints(breakable.transform.GetChild(1).gameObject));
            //breakable.transform.GetChild(2).GetComponent<Throwable>()
            //    .onPickUp.AddListener(() => interFunc.DeactivateRigidbodyConstraints(breakable.transform.GetChild(2).gameObject));
            //Instantiate the message
            */
            Destroy(this.gameObject);
        }
    }
}
