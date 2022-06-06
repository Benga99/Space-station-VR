using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DartsGame : MonoBehaviour
{
    public int darts = 0;

    private void OnTriggerEnter(Collider other)
    {
        if (other.gameObject.tag == "Dart")
        {
            other.gameObject.GetComponent<Rigidbody>().constraints = RigidbodyConstraints.FreezeAll;
            darts++;
        }
    }
}
