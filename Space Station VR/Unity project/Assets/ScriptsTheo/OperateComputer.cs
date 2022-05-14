using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class OperateComputer : MonoBehaviour
{
    [SerializeField]
    private GameObject key;

    private InteractableFunctionality interFunc;

    private bool fired = false;
    // Start is called before the first frame update
    void Start()
    {
        interFunc = FindObjectOfType<InteractableFunctionality>();
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void OnTriggerEnter(Collider other)
    {
        if(other.gameObject.tag == "Fire" && !fired)
        {
            interFunc.DeactivateRigidbodyConstraints(key);
            key.GetComponent<Rigidbody>().AddForce(-10f, 0, 0);
            Debug.Log("Force added");
            fired = true;
        }
    }

    private void OnCollisionEnter(Collision collision)
    {
        if (collision.gameObject.tag == "Fire" && !fired)
        {
            interFunc.DeactivateRigidbodyConstraints(key);
            key.GetComponent<Rigidbody>().AddForce(-10f, 0, 0);
            Debug.Log("Force added");
            fired = true;
        }
    }
}
