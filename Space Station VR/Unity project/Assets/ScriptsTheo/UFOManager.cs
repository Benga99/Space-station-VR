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

    bool collided = false;
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
        if(other.gameObject.tag == "Bullet" && !collided)
        {
            collided = true;
            UFOparent.UFOsDown++;
            audioExplosion.Play();
            Instantiate(explosionEffect, this.transform.position, this.transform.rotation);

            this.gameObject.SetActive(false);
        }
    }
}
