using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class UFOManager : MonoBehaviour
{
    [SerializeField]
    private GameObject explosionEffect;
    [SerializeField]
    private AudioSource audioExplosion;

    private UFOParentRotate UFOparent;

    float rotationFactor = 0;
    // Start is called before the first frame update
    void Start()
    {
        rotationFactor = Random.Range(-3f, 3f);
        UFOparent = FindObjectOfType<UFOParentRotate>();
    }

    // Update is called once per frame
    void Update()
    {
        this.gameObject.transform.Rotate(0, 0, rotationFactor, Space.Self);
    }

    private void OnTriggerEnter(Collider other)
    {
        if(other.gameObject.tag == "Bullet")
        {
            UFOparent.UFOsDown++;
            audioExplosion.Play();
            Instantiate(explosionEffect, this.transform.localPosition, this.transform.rotation);
            Destroy(this.gameObject);
        }
    }
}
