using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BulletCollisionTV : MonoBehaviour
{
    [SerializeField]
    private Material defaultMat;
    [SerializeField]
    private Material brokenMat;
    [SerializeField]
    private AudioSource breakingAudio;

    private bool collided = false;


    private void Start()
    {
        GetComponent<MeshRenderer>().material = defaultMat;
    }
    private void OnTriggerEnter(Collider other)
    {
        Debug.Log("entered");
        if (other.gameObject.tag == "Bullet" && !collided)
        {
            collided = true;
            GetComponent<MeshRenderer>().material = brokenMat;
            breakingAudio.Play();
        }
    }
}
