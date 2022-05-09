using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Touch : MonoBehaviour
{
    // Start is called before the first frame update
    public void OnCollisionEnter(Collision collision)
    {
        Debug.Log("Hand with " + collision.gameObject.name);
    }
}
